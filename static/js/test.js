
var btns = document.querySelectorAll('.ans_pole')
// Проходим по массиву
btns.forEach(function(btn) {
  // Вешаем событие клик
  btn.addEventListener('click', function(e) {
    console.log('Button clicked' + e.target.classList);
  })
})