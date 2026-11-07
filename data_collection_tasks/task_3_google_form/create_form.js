function createIAZGoogleForm() {
  // 1. Створюємо нову Google Форму
  var form = FormApp.create('Збір даних для ІАЗ ОУВ');
  form.setDescription('Форма оперативного збору звітної інформації з підрозділів.');

  // 2. Поле: Електронна пошта з перевіркою формату та обов'язковістю (Варіанти 3 та 6)
  var emailValidation = FormApp.createTextValidation()
    .requireTextIsEmail()
    .setHelpText('Введіть коректну адресу електронної пошти (наприклад, name@domain.com)')
    .build();
  
  form.addTextItem()
    .setTitle('Електронна пошта')
    .setRequired(true)
    .setValidation(emailValidation);

  // 3. Поле: Ім'я (ПІБ / Позивний)
  form.addTextItem()
    .setTitle('Ім’я (ПІБ відповідальної особи)')
    .setRequired(true);

  // 4. Поле: Дата подання
  form.addDateItem()
    .setTitle('Дата')
    .setRequired(true);

  // 5. Поле: Відділ / Підрозділ
  form.addListItem()
    .setTitle('Відділ / Секція штабу')
    .setChoiceValues(['J-1 (Персонал)', 'J-2 (Розвідка)', 'J-3 (Операції)', 'J-4 (Логістика)', 'J-6 (Зв’язок та ІС)'])
    .setRequired(true);

  // 6. Виводимо посилання на створену форму в журнал виконання
  Logger.log('Посилання для заповнення форми (Published URL): ' + form.getPublishedUrl());
  Logger.log('Посилання для редагування форми (Edit URL): ' + form.getEditUrl());
}