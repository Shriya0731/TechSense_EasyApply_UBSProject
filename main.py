from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse

#
# parser = reqparse.RequestParser()
#
app = Flask(__name__)


@app.route('/test', methods=['GET', 'POST'])
def home():
    if (request.method == 'GET'):
        data = "Its Working"
        return jsonify({'data': data})
# api = Api(app)
#
# STUDENTS = {}
#
#
#
#
# @app.route('/students/', methods=['GET'])
# def response():
#     s = StudentsList();
#     s.get()
#
#
#
# class StudentsList():
#
#   def get(self):
#       STUDENTS = {
#           '1': {'name': 'Mark', 'age': 23, 'spec': 'math'},
#           '2': {'name': 'Jane', 'age': 20, 'spec': 'biology'},
#           '3': {'name': 'Peter', 'age': 21, 'spec': 'history'},
#           '4': {'name': 'Kate', 'age': 22, 'spec': 'science'}, }
#       return STUDENTS
#   def post(self):
#       parser.add_argument("name")
#       parser.add_argument("age")
#       parser.add_argument("spec")
#       args = parser.parse_args()
#       student_id = int(max(STUDENTS.keys())) + 1
#       student_id = '%i' % student_id
#       STUDENTS[student_id] = {
#           "name": args["name"],
#           "age": args["age"],
#           "spec": args["spec"],
#       }
#       return STUDENTS[student_id], 201

if __name__ == "__main__":
  app.run(debug=True)