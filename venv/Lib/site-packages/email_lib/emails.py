"""
Email Organization
"""

from imaplib import IMAP4_SSL
from email import message_from_string
from email.utils import parsedate_to_datetime
from datetime import timedelta
from collections import defaultdict

from pytz import timezone

from .hashtags import extract_hashtags

UTC = timezone('UTC')


class EmailLogicError(Exception):
    """
    Package-specific error
    """
    pass


class EmailClient:
    """
    IMAP client Abstraction class
    * server (string): imap server URL
    * account (string): account to log in against
    * password (string): associated password of the account
    """

    def __init__(self, server, account, password):
        self.server = server
        self.account = account
        self.password = password

        self.client = IMAP4_SSL(self.server)

    def login(self):
        """
        Initiate loging in against the email server
        """
        try:
            self.client.login(self.account, self.password)
        except IMAP4_SSL.error:
            raise EmailLogicError("Invalid imap login to {} for account {}".format(
                self.server, self.account))

    def set_mailbox(self, mailbox):
        """
        Select a mailbox to work on
        * mailbox: name of the mailbox to look up to
        """
        value = self.client.select(mailbox, readonly=True)

        if value[0] != 'OK':
            raise EmailLogicError(
                "Could not connect to mailbox {}".format(mailbox))

    def search(self, query):
        """
        Search emails on the IMAP server
        * query (string): rfc3501 compatible search query
        """
        status, result = self.client.search(None, query)

        if status != 'OK':
            raise EmailLogicError("Couldn't find results for that time range")

        if len(result[0]) == 0:
            return []

        email_ids = result[0].decode().split(' ')


        # Fetch all emails at once
        status, messages = self.client.fetch(','.join(email_ids), '(RFC822)')

        if status != 'OK':
            raise EmailLogicError('Could not fetch messages')

        # Filter messages, imaplib returns the last parenthesis
        # if it's having its own line before carriage return
        # https://stackoverflow.com/questions/34542742/why-does-imaplib-return-a-lone-parenthesis-after-each-email?answertab=votes#tab-top
        messages = [message for message in messages if message != b')']

        for fmt, raw_message in messages:
            message = message_from_string(raw_message.decode('UTF-8'))
            yield EmailMessage(message)


class EmailQueryBuilder:
    """
    Helper that abstracts rfc3501 query build
    """

    def __init__(self):
        self.query_items = []

    def build(self):
        """
        Return rfc 3501 compatible search query
        """
        return ' '.join(self.query_items)

    def start(self, start_date):
        """
        Add a search criteria since a starting date
        * start_date (datetime): starting date for the search
        """
        self.query_items.append('(SINCE {})'.format(
            start_date.strftime('%d-%b-%Y')))
        return self

    def stop(self, stop_date):
        """
        Add a search criteria before an end date
        * stop_date (datetime): starting date for the search
        """
        self.query_items.append('(BEFORE {})'.format(
            stop_date.strftime('%d-%b-%Y')))
        return self

    def subject(self, prefix):
        """
        Add a search criteria to match the subject against a given prefix
        * prefix (string): prefix or complete subject to be matched
        """
        self.query_items.append('(SUBJECT "{}")'.format(prefix))
        return self

    def from_addr(self, from_str):
        """
        Add a search criteria to match the from sending addr to the given parameter
        * from_str (string): from address to match against
        """
        self.query_items.append('(FROM {})'.format(from_str))
        return self


class EmailOrganizer:
    """
    Transforms a list of emails into threads
    """

    def __init__(self, emails):
        """
        * emails (iterator): List of EmailMessage to be processed
        """
        self.emails = emails

    def organize(self):
        """
        Organize a list of EmailMessage into threads
        Returns
        * threads (defaultdict): mapping of email subjects (string) -> list(EmailThread)
        * orphans (list(EMailMessage)): emails not belonging to a thread

        threads is a mapping of subject -> thread list because
        two different threads with the same subject can occur within the same
        retrieval.

        An example could be an Alert happening multiple times in a day.
        """
        threads = defaultdict(lambda: [])
        messages = []

        # If email is first (no reference), the thread is created, otherwise
        # it's an unaffected email
        for message in self.emails:
            if message.is_thread:
                thread = EmailThread()
                thread.add(message)
                threads[thread.subject].append(thread)
            else:
                messages.append(message)

        # sort emails to guaratee in-order thread assignments
        messages = sorted(messages, key=lambda x: x.date)
        orphans = []

        for message in messages:
            is_orphan = True
            for topic in threads.values():
                for thread in topic:
                    if thread.try_add(message):
                        is_orphan = False
                        break
                if not is_orphan:
                    break
            if is_orphan:
                orphans.append(message)

        return threads, orphans


class EmailScraper:
    """
    Retrieve all email threads during a time window
    """

    def __init__(self, client):
        self.client = client

    def scrape(self, mailbox, prefix, start, stop):
        """
        Fetch emails from a mailbox corresponding to a patter
        * mailbox: name of the mailbox to scane
        * prefix: pattern to match against
        * start: datetime from when to start scanning
        * stop: datetime from when to stop scanning
        """
        self.client.set_mailbox(mailbox)

        # start_utc can be set to prior time
        # due to rfc3501 date search field accepting only dates
        start_utc = start.astimezone(UTC)
        stop_utc = stop.astimezone(UTC)

        days_diff = (stop_utc-start_utc).days

        if days_diff < 0:
            raise EmailLogicError('Stop must be after Start')

        if days_diff < 1:
            start_utc = stop_utc - timedelta(days=1)

        query = EmailQueryBuilder().start(start_utc).stop(
            stop_utc).subject(prefix).build()

        return EmailOrganizer(self.client.search(query)).organize()


class EmailThread:
    """
    Abstract an email thread
    """

    def __init__(self):
        self.subject = None
        self.messages = {}
        self.first_message_id = None
        self._tags = set()
        self.tag_users = {}

    @property
    def first(self):
        """
        Return the thread originator
        """
        return self.messages[self.first_message_id]

    @property
    def date(self):
        if self.first_message_id:
            return self.first.date
        return None

    def has(self, query):
        """
        Search if queried message is in the thread
        * query (EMailMessage|str): criteria for email matching
        """
        if isinstance(query, EmailMessage):
            return self.has_message(query)
        return self.has_message_id(str(query))


    def has_message(self, message):
        """
        Check if presented message references an existing thread message
        * message (EmailMessage)
        """
        for message_id, msg in self.messages.items():
            if (message_id in message.references
                    or message.message_id in msg.references):
                return True

        return False


    def has_message_id(self, message_id):
        """
        Check if a message in the thread has a certain message_id
        * message_id (string)
        """
        return message_id in self.messages.keys()

    def add(self, message):
        """
        Add a message to the thread list
        * message (EmaiMessage)
        """

        if message.is_thread:
            self.subject = message.subject
            self.first_message_id = message.message_id

        self.messages[message.message_id] = message

    def try_add(self, message):
        """
        Try to add a message by checking if it belongs to the thread
        * message (EmailMessage)
        """
        if self.has(message) or self.first_message_id is None:
            self.add(message)
            return True
        return False

    @property
    def tags(self):
        """
        Returns the list of tags applied to this incident email thread
        """
        if not self._tags:
            for message in self:
                self._tags.update(message.tags)
                for tag in message.tags:
                    if tag not in self.tag_users:
                        self.tag_users[tag] = message.from_addr
        return self._tags

    def __str__(self):
        return '{}: {}'.format(self.subject, self.date.strftime("%Y-%m-%dT%H:%M:%SZ"))

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.messages)

    def __iter__(self):
        for item in sorted(self.messages.values(), key=lambda x: x.date):
            yield item


class EmailMessage:
    """
    Represent an email message
    """

    def __init__(self, message):
        """
        * email (email.message.Message): email message representation
        """
        self.message = message

        self.subject = message['Subject'].replace('\r\n', '')
        self.topic = self.subject.replace('Re: ', '')
        self.from_addr = message['From']
        self.to_addrs = [addr.strip() for addr in message['To'].split(',')]
        self.message_id = message['Message-Id'].strip()
        self._references = None
        self.date = parsedate_to_datetime(message['Date']).astimezone(UTC)
        self.is_thread = not self.references
        self._content = None
        self._tags = set()

    @property
    def references(self):
        """
        Extract and sanitize references
        """
        if self._references is None:
            self._references = []
            raw_references = self.message.get('References')
            if raw_references:
                self._references.extend(
                    raw_references.replace('\r\n', '').strip().split(' ')
                )

        return self._references

    @property
    def content(self):
        """
        Lazily generates and returns the content of the email message
        """

        if not self._content:
            self._content = ''
            for part in self.message.get_payload():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    self._content += str(part)
        return self._content

    @property
    def tags(self):
        """
        Returns the tags associated with the email
        """
        if not self._tags:
            tags = extract_hashtags(self.content)
            if tags:
                self._tags.update(tags)
        return self._tags

    def __str__(self):
        return '{}: {}: {}'.format(
            self.__class__.__name__,
            self.subject,
            self.date.strftime("%Y-%m-%dT%H:%M:%SZ")
        )

    def __repr__(self):
        return str(self)
