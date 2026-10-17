const confirmation = document.getElementById('confirmation');
if (confirmation) {
  confirmation.removeAttribute('open');
  confirmation.showModal();
  const edit = () => {
    confirmation.close();
    document.getElementById('id_email').focus();
  };
  document.getElementById('edit-email').addEventListener('click', edit);
  confirmation.addEventListener('cancel', edit);
}
