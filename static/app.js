const num = document.getElementByName('.number')
const numVal = Number(num.getAttribute('data-value'))
let counter = 0
setInterval(() => {
if (counter !== numVal) {
counter++
num.innerHTML = `${counter}%`
}
}, 80)