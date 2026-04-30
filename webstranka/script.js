// Small JS for year, form handling and simple interactions
document.addEventListener('DOMContentLoaded',function(){
  const y = document.getElementById('year');
  if(y) y.textContent = new Date().getFullYear();

  const form = document.getElementById('contactForm');
  const msg = document.getElementById('formMessage');
  if(form){
    form.addEventListener('submit',function(e){
      e.preventDefault();
      const name = document.getElementById('name').value.trim();
      const email = document.getElementById('email').value.trim();
      const message = document.getElementById('message').value.trim();
      if(!name || !email || !message){
        msg.textContent = 'Vyplňte prosím všetky polia.';
        msg.style.color = 'red';
        return;
      }
      // Since no backend is configured, show a success message.
      form.reset();
      msg.style.color = 'green';
      msg.textContent = 'Ďakujeme! Vaša správa bola odoslaná (lokálne).';
    });
  }
});
