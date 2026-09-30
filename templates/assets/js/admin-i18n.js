(() => {
  'use strict';
  // Russian is the source language of the admin markup. Each entry is [Uzbek, English].
  const words = {
    'Админка':['Boshqaruv paneli','Admin panel'], 'админка':['boshqaruv paneli','admin panel'],
    'Пароль':['Parol','Password'], 'Войти':['Kirish','Sign in'], 'Выйти':['Chiqish','Sign out'],
    'Экраны':['Ekranlar','Screens'], 'Экран':['Ekran','Screen'], 'Новый экран':['Yangi ekran','New screen'],
    'Флагманы':['Flagmanlar','Flagships'], 'Флагман':['Flagman','Flagship'], 'Флагманская сеть':['Flagmanlar tarmog‘i','Flagship network'],
    'Аэропорт':['Aeroport','Airport'], 'Аэропорт «Ташкент»':['«Toshkent» aeroporti','Tashkent Airport'],
    'Курс и контакты':['Kurs va kontaktlar','Exchange rate and contacts'], 'Тексты сайта':['Sayt matnlari','Site text'],
    'Открыть сайт ↗':['Saytni ochish ↗','Open site ↗'], 'Фото':['Surat','Photo'],
    'Название':['Nomi','Name'], 'Подпись под названием':['Nom ostidagi izoh','Subtitle'],
    '(необязательно, например «перекрёсток»)':['(ixtiyoriy, masalan «chorraha»)','(optional, e.g. “intersection”)'],
    'Русский':['Ruscha','Russian'], 'Русский *':['Ruscha *','Russian *'],
    'Параметры':['Parametrlar','Specifications'], 'Параметры и цена':['Parametrlar va narx','Specifications and price'],
    'Размер':['O‘lcham','Size'], 'как на сайте, «8 × 4 м»':['saytdagidek, «8 × 4 m»','as shown on site, “8 × 4 m”'],
    'Площадь, м²':['Maydon, m²','Area, m²'], 'считается из размера':['o‘lchamdan hisoblanadi','calculated from size'],
    'Разрешение':['Aniqlik','Resolution'], 'Время трансляции':['Efir vaqti','Broadcast hours'],
    'Показов в месяц':['Oylik namoyishlar','Plays per month'], 'Размер для КП':['Taklifdagi o‘lcham','Size in offer'],
    'если отличается':['farq qilsa','if different'], 'Категория':['Toifa','Category'],
    'определяется площадью':['maydonga qarab aniqlanadi','based on area'], 'номер фото c{ID}.jpg':['surat raqami c{ID}.jpg','photo number c{ID}.jpg'],
    'Цены за 1 месяц, сум без НДС':['1 oylik narx, so‘m, QQSsiz','Monthly prices, UZS excluding VAT'],
    '— пустое поле: длительности нет':['— bo‘sh maydon: bu davomiylik yo‘q','— blank means this duration is unavailable'],
    'Ролик 5 сек':['5 soniyalik rolik','5 sec spot'], 'Ролик 10 сек':['10 soniyalik rolik','10 sec spot'],
    'Ролик 15 сек':['15 soniyalik rolik','15 sec spot'], 'Ролик 20 сек':['20 soniyalik rolik','20 sec spot'],
    'Адрес для коммерческого предложения (Excel)':['Tijorat taklifi uchun manzil (Excel)','Address for commercial offer (Excel)'],
    '(НАЗВАНИЕ) Район, пересечение улиц …':['(NOMI) Tuman, ko‘chalar chorrahasi …','(NAME) District, street intersection …'],
    'Удалить экран':['Ekranni o‘chirish','Delete screen'], 'Удалить формат':['Formatni o‘chirish','Delete format'],
    'Отмена':['Bekor qilish','Cancel'], 'Сохранить':['Saqlash','Save'], 'Сбросить':['Tiklash','Reset'],
    'Формат аэропорта':['Aeroport formati','Airport format'], 'Новый формат':['Yangi format','New format'],
    'Зона (заголовок формата)':['Hudud (format sarlavhasi)','Zone (format heading)'],
    'Тип носителя':['Tashuvchi turi','Display type'], 'Терминал':['Terminal','Terminal'],
    'Кол-во носителей':['Tashuvchilar soni','Number of displays'], 'Показы':['Namoyishlar','Plays'],
    'Ролик, сек':['Rolik, soniya','Spot, sec'], 'Цена за месяц, сум':['Oylik narx, so‘m','Monthly price, UZS'],
    'Прогноз охвата, человек':['Taxminiy qamrov, kishi','Estimated reach, people'],
    'Неделя':['Hafta','Week'], 'Месяц':['Oy','Month'], 'Год':['Yil','Year'],
    'Фото экрана':['Ekran surati','Screen photo'], 'Фото формата':['Format surati','Format photo'],
    'Закрыть':['Yopish','Close'], 'Выше':['Yuqoriga','Move up'], 'Ниже':['Pastga','Move down'], 'Убрать':['Olib tashlash','Remove'],
    'JPG, PNG или WEBP до 12 МБ. Фото сохранится сразу, ширина будет уменьшена до 1600 px. Лучше горизонтальное 16:10.':['12 MB gacha JPG, PNG yoki WEBP. Surat darhol saqlanadi va eni 1600 px gacha kichraytiriladi. Gorizontal 16:10 tavsiya etiladi.','JPG, PNG or WEBP up to 12 MB. The photo saves immediately and is resized to 1600 px wide. Landscape 16:10 is recommended.'],
    'Фото сохранится сразу. Лучше формат 4:3.':['Surat darhol saqlanadi. 4:3 format tavsiya etiladi.','The photo saves immediately. A 4:3 ratio is recommended.'],
    'Поиск по названию, адресу, ID':['Nom, manzil yoki ID bo‘yicha qidirish','Search by name, address or ID'],
    'Вид списка':['Ro‘yxat ko‘rinishi','List view'], '▤ Таблица':['▤ Jadval','▤ Table'], '▦ Карточки':['▦ Kartochkalar','▦ Cards'],
    'Формат':['Format','Format'],
    'Поиск по тексту':['Matn bo‘yicha qidirish','Search text'], 'Ничего не найдено':['Hech narsa topilmadi','No results'],
    'Название':['Nomi','Name'], 'Изменить':['Tahrirlash','Edit'], '5 сек':['5 soniya','5 sec'],
    '10 сек':['10 soniya','10 sec'], '15 сек':['15 soniya','15 sec'], '20 сек':['20 soniya','20 sec'],
    'Городской':['Shahar ekrani','City screen'], 'Крупный':['Yirik ekran','Large screen'],
    '+ Добавить экран':['+ Ekran qo‘shish','+ Add screen'], '+ Добавить формат':['+ Format qo‘shish','+ Add format'],
    '+ Добавить экран во флагманы…':['+ Flagmanlarga ekran qo‘shish…','+ Add screen to flagships…'],
    'Порядок флагманов изменён':['Flagmanlar tartibi o‘zgardi','Flagship order changed'],
    'Экраны в блоке «Флагманы» на главной, сверху вниз. Рекомендуем 4–8.':['Bosh sahifadagi flagman ekranlar yuqoridan pastga ko‘rsatiladi. 4–8 ta tavsiya etiladi.','Flagship screens on the home page, top to bottom. We recommend 4–8.'],
    'Сохранено. На сайте изменения видны сразу':['Saqlandi. O‘zgarishlar saytda darhol ko‘rinadi','Saved. Changes appear on the site immediately'],
    'Сервер не отвечает':['Server javob bermayapti','Server is not responding'],
    'Нужно войти':['Tizimga kirish kerak','Sign in required'], 'Нужно войти в систему':['Tizimga kirish kerak','Sign in required'],
    'Ошибка сервера':['Server xatosi','Server error'], 'Неверный пароль':['Parol noto‘g‘ri','Incorrect password'],
    'Фото больше 12 МБ':['Surat 12 MB dan katta','Photo exceeds 12 MB'],
    'Нужен JPG, PNG или WEBP':['JPG, PNG yoki WEBP kerak','Use JPG, PNG or WEBP'],
    'Объект не найден':['Ma’lumot topilmadi','Item not found'],
    'Сохраняю…':['Saqlanmoqda…','Saving…'], 'Сначала сохраните или сбросьте изменения в текстах':['Avval matn o‘zgarishlarini saqlang yoki bekor qiling','Save or discard text changes first'],
    'Укажите название на русском':['Ruscha nomini kiriting','Enter the Russian name'],
    'Укажите хотя бы одну цену':['Kamida bitta narx kiriting','Enter at least one price'],
    'Сохранено. Не забудьте загрузить фото экрана':['Saqlandi. Ekran suratini yuklashni unutmang','Saved. Remember to upload the screen photo'],
    'Сначала сохраните экран, затем загрузите фото':['Avval ekranni saqlang, keyin surat yuklang','Save the screen before uploading a photo'],
    'Загружаю фото…':['Surat yuklanmoqda…','Uploading photo…'], 'Фото обновлено':['Surat yangilandi','Photo updated'],
    'Экран удалён':['Ekran o‘chirildi','Screen deleted'], 'Формат удалён':['Format o‘chirildi','Format deleted'],
    'Удалить без возможности отмены?':['Qaytarib bo‘lmaydigan qilib o‘chirilsinmi?','Delete permanently?'],
    'Да, удалить':['Ha, o‘chirish','Yes, delete'], 'Нет':['Yo‘q','No'],
    'Нужен хотя бы один флагман':['Kamida bitta flagman kerak','At least one flagship is required'],
    'Укажите название зоны на русском':['Hududning ruscha nomini kiriting','Enter the Russian zone name'],
    'Формат добавлен. Загрузите фото':['Format qo‘shildi. Surat yuklang','Format added. Upload a photo'],
    'Сначала сохраните формат, затем загрузите фото':['Avval formatni saqlang, keyin surat yuklang','Save the format before uploading a photo'],
    'Курс влияет на цены английской версии и Excel-КП на английском.':['Kurs inglizcha saytdagi va Excel taklifidagi narxlarga ta’sir qiladi.','The rate affects prices on the English site and in the English Excel offer.'],
    'Цены в долларах (английская версия)':['Dollar narxlari (inglizcha versiya)','Prices in USD (English version)'],
    'Курс, сум за $1':['Kurs, 1 dollar uchun so‘m','Rate, UZS per $1'],
    'Множитель «с налогами»':['«Soliqlar bilan» koeffitsiyenti','“Including tax” multiplier'],
    'НДС для Excel-КП, %':['Excel taklifida QQS, %','VAT in Excel offer, %'],
    'сейчас зафиксирован в шаблоне КП (12%)':['hozir taklif shablonida 12% belgilangan','currently fixed at 12% in the offer template'],
    'Контакты на сайте':['Saytdagi kontaktlar','Site contacts'], 'Телефон':['Telefon','Phone'],
    'Instagram (как показывать)':['Instagram (ko‘rinishi)','Instagram (display name)'],
    'Ссылка для всех контактов':['Barcha kontaktlar havolasi','Link for all contacts'],
    'куда ведут клики по телефону, почте, Instagram и адресу':['telefon, email, Instagram va manzil bosilganda ochiladi','opened when phone, email, Instagram or address is clicked'],
    'Адрес меняется во вкладке «Тексты сайта»: ключи':['Manzil «Sayt matnlari» bo‘limida o‘zgaradi: kalitlar','Edit the address under “Site text”: keys'],
    'Введите курс и множитель':['Kurs va koeffitsiyentni kiriting','Enter the rate and multiplier'],
    'Проверьте курс и множитель':['Kurs va koeffitsiyentni tekshiring','Check the rate and multiplier'],
    'Все надписи страницы на трёх языках. Цены, названия экранов и форматы меняются в своих вкладках.':['Sahifadagi barcha yozuvlar uch tilda. Narxlar, ekran nomlari va formatlar o‘z bo‘limlarida o‘zgaradi.','All page text in three languages. Edit prices, screen names and formats in their own tabs.'],
    'Можно использовать теги':['Quyidagi teglarni ishlatish mumkin','You can use these tags'],
    '(перенос строки)':['(yangi qator)','(line break)'], '(красный цвет)':['(qizil rang)','(red color)'],
    'Подстановки:':['O‘zgaruvchilar:','Placeholders:'], '— число экранов,':['— ekranlar soni,','— number of screens,'],
    '— число носителей в аэропорту,':['— aeroportdagi tashuvchilar soni,','— number of airport displays,'],
    '— курс доллара.':['— dollar kursi.','— dollar exchange rate.'],
    'Верхнее меню':['Yuqori menyu','Top menu'], 'Первый экран':['Birinchi sahifa','Hero section'],
    'Цифры под табло':['Tablo ostidagi raqamlar','Numbers below the display'], 'Каталог':['Katalog','Catalogue'],
    'Мобильный LED':['Mobil LED','Mobile LED'], 'Презентации PDF':['PDF taqdimotlar','PDF presentations'],
    'Контакты':['Kontaktlar','Contacts'], 'Условия оплаты':['To‘lov shartlari','Payment terms'],
    'Подвал':['Pastki qism','Footer'], 'Панель медиаплана':['Media reja paneli','Media plan panel'],
    'Прочее':['Boshqa','Other'], 'Отменить изменения':['O‘zgarishlarni bekor qilish','Discard changes'],
    'Сохранить тексты':['Matnlarni saqlash','Save text'],
    'Выделите текст и выберите оформление. Кнопки с числами вставляют данные, которые обновляются на сайте автоматически.':['Matnni belgilang va ko‘rinishini tanlang. Raqamli tugmalar saytda avtomatik yangilanadigan ma’lumotlarni qo‘shadi.','Select text and choose its style. Number buttons insert values that update automatically on the site.'],
    'Оформление текста':['Matnni bezash','Text formatting'],
    'Жирный текст':['Qalin matn','Bold text'],
    'Курсив':['Qiya matn','Italic'],
    'Красный акцент':['Qizil urg‘u','Red accent'],
    'Новая строка':['Yangi qator','New line'],
    'Число экранов':['Ekranlar soni','Number of screens'],
    'Число носителей в аэропорту':['Aeroportdagi tashuvchilar soni','Number of airport displays'],
    'Курс доллара':['Dollar kursi','Dollar exchange rate'],
    'Текст сайта':['Sayt matni','Site text'],
    'Введите текст…':['Matn kiriting…','Enter text…'],
    '# Экраны':['# Ekranlar','# Screens'],
    '# Аэропорт':['# Aeroport','# Airport'],
    '$ Курс':['$ Kurs','$ Rate'],
    'Сначала выделите текст':['Avval matnni belgilang','Select text first']
  };
  const patterns = [
    [/^(\d+) экранов в городе\. Цены в сумах за месяц без НДС\.$/, n => [`Shaharda ${n} ta ekran. Oylik narxlar so‘mda, QQSsiz.`, `${n} city screens. Monthly prices in UZS excluding VAT.`]],
    [/^(\d+) форматов, (\d+) носителей\. Число носителей на сайте считается автоматически\.$/, (a,b) => [`${a} ta format, ${b} ta tashuvchi. Saytdagi tashuvchilar soni avtomatik hisoblanadi.`, `${a} formats, ${b} displays. The site calculates the display count automatically.`]],
    [/^Формат (\d+)(.*)$/, (n,rest) => [`Format ${n}${rest}`, `Format ${n}${rest}`]],
    [/^Экран · (.*)$/, n => [`Ekran · ${n}`, `Screen · ${n}`]],
    [/^Изменено текстов: (\d+)$/, n => [`O‘zgargan matnlar: ${n}`, `Changed texts: ${n}`]],
    [/^≈ (.*) в англ\. версии$/, n => [`≈ ${n} inglizcha versiyada`, `≈ ${n} in English version`]],
    [/^(.*\d+) шт\.$/, n => [`${n} dona`, `${n} pcs`]],
    [/^([\d\s]+) сум$/, n => [`${n} so‘m`, `${n} UZS`]],
    [/^Цена (\d+) сек: введите число$/, n => [`${n} soniyalik narx: son kiriting`, `${n} sec price: enter a number`]],
    [/^Пример: экран (.*) на английском сайте\.$/, n => [`Misol: ${n} inglizcha saytda.`, `Example: ${n} on the English site.`]],
  ];
  const source = new WeakMap();
  const attributes = new WeakMap();
  let language;
  try { language = localStorage.getItem('ahx_admin_lang') || 'uz'; } catch (_) { language = 'uz'; }
  if (!['uz','en','ru'].includes(language)) language = 'uz';

  function translate(raw) {
    if (language === 'ru') return raw;
    const trimmed = raw.trim();
    if (!trimmed) return raw;
    const idx = language === 'uz' ? 0 : 1;
    let value = words[trimmed]?.[idx];
    if (!value) for (const [regex, output] of patterns) {
      const match = trimmed.match(regex);
      if (match) { value = output(...match.slice(1))[idx]; break; }
    }
    return value ? raw.replace(trimmed, value) : raw;
  }
  function walk(root) {
    if (root.nodeType === Node.TEXT_NODE) {
      if (root.parentElement?.closest('script,style,textarea,[contenteditable]')) return;
      if (!source.has(root)) source.set(root, root.textContent);
      const value = translate(source.get(root));
      if (root.textContent !== value) root.textContent = value;
      return;
    }
    if (root.nodeType !== Node.ELEMENT_NODE || root.matches('script,style,textarea')) return;
    if (!attributes.has(root)) attributes.set(root, Object.fromEntries(['title','placeholder','aria-label','data-placeholder'].filter(a => root.hasAttribute(a)).map(a => [a, root.getAttribute(a)])));
    for (const [name, value] of Object.entries(attributes.get(root))) {
      const translated = translate(value);
      if (root.getAttribute(name) !== translated) root.setAttribute(name, translated);
    }
    if (!root.matches('[contenteditable]')) for (const child of [...root.childNodes]) walk(child);
  }
  function refresh() {
    document.documentElement.lang = language === 'uz' ? 'uz-Latn' : language;
    document.title = language === 'uz' ? 'LED CITY · Boshqaruv paneli' : language === 'en' ? 'LED CITY · Admin panel' : 'LED CITY · Админка';
    walk(document.body);
  }
  function setLanguage(next) {
    if (!['uz','en','ru'].includes(next)) return;
    language = next;
    try { localStorage.setItem('ahx_admin_lang', next); } catch (_) {}
    refresh();
  }
  const observer = new MutationObserver(records => {
    for (const record of records) {
      if (record.type === 'characterData') {
        const node = record.target;
        const current = node.textContent;
        const original = source.get(node);
        if (current !== translate(original ?? current)) source.set(node, current);
        walk(node);
      } else for (const node of record.addedNodes) walk(node);
    }
  });
  observer.observe(document.body, {childList:true, characterData:true, subtree:true});
  window.adminI18n = {get language(){ return language; }, setLanguage, refresh, translate};
  refresh();
})();
