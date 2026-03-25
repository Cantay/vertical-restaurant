import base64
import os
from odoo import models

IMG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'src', 'img')


def _load_image(filename):
    """Load image from static/src/img/ and return base64 encoded string."""
    filepath = os.path.join(IMG_PATH, filename)
    if os.path.isfile(filepath):
        with open(filepath, 'rb') as f:
            return base64.b64encode(f.read())
    return False


# Category name → image file mapping
CATEGORY_IMAGES = {
    'Burgerler': 'combo-hamb.png',
    'Yan Ürünler': 'th-mozza.png',
    'İçecekler': 'drink_category.png',
    'Tatlılar': 'th-milkshake_banana.png',
    'Pideler': 'food_category.png',
    'Lahmacunlar': 'food_category.png',
    'Salatalar': 'th-club.png',
    'Sushi Setleri': 'th-salmon.png',
    'Ramen': 'th-pasta.png',
    'Başlangıçlar': 'th-mozza.png',
    'Pizzalar': 'th-pizza.png',
    'Makarnalar': 'th-pasta.png',
    'Ana Yemekler': 'food_category.png',
    'Çorbalar': 'food_category.png',
    'Zeytinyağlılar': 'food_category.png',
}


class FoodDemoDataLoader(models.AbstractModel):
    _name = 'food.demo.data.loader'
    _description = 'Food Demo Data Loader'

    def _get_demo_restaurants(self):
        return [
            {
                'xmlid': 'demo_restaurant_burger_house',
                'name': 'Burger House',
                'description': 'El yapımı gurme burgerler ve özel soslarla hazırlanan lezzetler.',
                'phone': '+90 212 555 0101',
                'address': 'Beyoğlu, İstiklal Caddesi No:42, İstanbul',
                'always_open': True,
                'is_popular': True,
                'is_fast_delivery': True,
                'delivery_fee': 15.0,
                'delivery_time_min': 20,
                'delivery_time_max': 35,
                'min_order_amount': 80.0,
                'platform_commission_rate': 15.0,
                'image_1920': _load_image('combo-hamb.png'),
                'categories': ['Burgerler', 'Yan Ürünler', 'İçecekler', 'Tatlılar'],
                'work_hours': [],
            },
            {
                'xmlid': 'demo_restaurant_pide_ustasi',
                'name': 'Pide Ustası',
                'description': 'Karadeniz usulü pide ve lahmacun. Odun fırınında pişen geleneksel lezzetler.',
                'phone': '+90 212 555 0202',
                'address': 'Kadıköy, Moda Caddesi No:18, İstanbul',
                'always_open': True,
                'is_popular': True,
                'delivery_fee': 10.0,
                'delivery_time_min': 25,
                'delivery_time_max': 40,
                'min_order_amount': 60.0,
                'platform_commission_rate': 12.0,
                'image_1920': _load_image('food_category.png'),
                'categories': ['Pideler', 'Lahmacunlar', 'Salatalar', 'İçecekler'],
                'work_hours': [],
            },
            {
                'xmlid': 'demo_restaurant_sushi_zen',
                'name': 'Sushi Zen',
                'description': 'Taze malzemelerle hazırlanan otantik Japon mutfağı. Sushi, sashimi ve ramen.',
                'phone': '+90 212 555 0303',
                'address': 'Beşiktaş, Barbaros Bulvarı No:55, İstanbul',
                'always_open': True,
                'is_fast_delivery': True,
                'delivery_fee': 20.0,
                'delivery_time_min': 30,
                'delivery_time_max': 45,
                'min_order_amount': 120.0,
                'platform_commission_rate': 18.0,
                'image_1920': _load_image('th-salmon.png'),
                'categories': ['Sushi Setleri', 'Ramen', 'Başlangıçlar', 'İçecekler'],
                'work_hours': [],
            },
            {
                'xmlid': 'demo_restaurant_pizza_napoli',
                'name': 'Pizza Napoli',
                'description': 'İtalyan usulü taş fırın pizza. Napoli hamuruyla hazırlanan gerçek İtalyan lezzeti.',
                'phone': '+90 212 555 0404',
                'address': 'Şişli, Halaskârgazi Caddesi No:120, İstanbul',
                'always_open': True,
                'has_campaign': True,
                'delivery_fee': 0.0,
                'delivery_time_min': 20,
                'delivery_time_max': 30,
                'min_order_amount': 70.0,
                'platform_commission_rate': 14.0,
                'image_1920': _load_image('th-pizza.png'),
                'categories': ['Pizzalar', 'Makarnalar', 'Salatalar', 'Tatlılar', 'İçecekler'],
                'work_hours': [],
            },
            {
                'xmlid': 'demo_restaurant_ev_yemekleri',
                'name': 'Annemin Mutfağı',
                'description': 'Ev yapımı Türk mutfağı. Günlük taze pişen yemekler, çorbalar ve zeytinyağlılar.',
                'phone': '+90 212 555 0505',
                'address': 'Üsküdar, Bağlarbaşı Caddesi No:7, İstanbul',
                'always_open': True,
                'is_popular': True,
                'delivery_fee': 5.0,
                'delivery_time_min': 25,
                'delivery_time_max': 40,
                'min_order_amount': 50.0,
                'platform_commission_rate': 10.0,
                'image_1920': _load_image('th-club.png'),
                'categories': ['Ana Yemekler', 'Çorbalar', 'Zeytinyağlılar', 'İçecekler'],
                'work_hours': [],
            },
        ]

    def _get_demo_products(self):
        return {
            'demo_restaurant_burger_house': {
                'Burgerler': [
                    {'name': 'Classic Burger', 'price': 120.0, 'desc': 'Dana köfte, marul, domates, turşu, özel sos',
                     'image': 'th-burger.png',
                     'addons': [
                         ('Ek Malzeme', 'Ekstra Peynir', 15.0, 'select'),
                         ('Ek Malzeme', 'Bacon', 20.0, 'select'),
                         ('Ek Malzeme', 'Jalapeno', 10.0, 'select'),
                         ('Burger Boyutu', 'Double Köfte', 40.0, 'select'),
                     ]},
                    {'name': 'Cheese Burger', 'price': 135.0, 'desc': 'Dana köfte, çift cheddar, karamelize soğan',
                     'image': 'th-cheeseburger.png'},
                    {'name': 'BBQ Burger', 'price': 145.0, 'desc': 'Dana köfte, BBQ sos, çıtır soğan halkası, bacon',
                     'image': 'combo-hamb.png'},
                    {'name': 'Tavuk Burger', 'price': 110.0, 'desc': 'Çıtır tavuk, marul, mayo, turşu',
                     'image': 'th-sandwich.png'},
                ],
                'Yan Ürünler': [
                    {'name': 'Patates Kızartması', 'price': 40.0, 'desc': 'Çıtır patates, özel baharat',
                     'image': 'th-mozza.png'},
                    {'name': 'Soğan Halkası', 'price': 45.0, 'desc': 'Çıtır pane soğan halkaları',
                     'image': 'th-mozza.png'},
                    {'name': 'Nugget (6 adet)', 'price': 55.0, 'desc': 'Tavuk nugget, ranch sos',
                     'image': 'th-sandwich.png'},
                ],
                'İçecekler': [
                    {'name': 'Coca-Cola 330ml', 'price': 25.0, 'desc': '', 'image': 'th-coke.png'},
                    {'name': 'Ayran', 'price': 15.0, 'desc': 'Ev yapımı ayran', 'image': 'th-water.png'},
                    {'name': 'Limonata', 'price': 30.0, 'desc': 'Taze sıkılmış limonata',
                     'image': 'th-minute_maid.png'},
                ],
                'Tatlılar': [
                    {'name': 'Brownie', 'price': 50.0, 'desc': 'Çikolatalı brownie, dondurma ile',
                     'image': 'th-milkshake_banana.png'},
                ],
            },
            'demo_restaurant_pide_ustasi': {
                'Pideler': [
                    {'name': 'Kaşarlı Pide', 'price': 90.0, 'desc': 'Bol kaşar peynirli, tereyağlı',
                     'image': 'food_category.png',
                     'addons': [
                         ('Ekstra', 'Yumurta', 10.0, 'select'),
                         ('Ekstra', 'Sucuk', 15.0, 'select'),
                         ('Ekstra', 'Pastırma', 20.0, 'select'),
                     ]},
                    {'name': 'Kuşbaşılı Pide', 'price': 130.0, 'desc': 'Dana kuşbaşı, biber, domates',
                     'image': 'food_category.png'},
                    {'name': 'Karışık Pide', 'price': 140.0, 'desc': 'Kuşbaşı, kaşar, biber, domates, yumurta',
                     'image': 'food_category.png'},
                    {'name': 'Sucuklu Pide', 'price': 110.0, 'desc': 'Sucuk, kaşar, yumurta',
                     'image': 'food_category.png'},
                ],
                'Lahmacunlar': [
                    {'name': 'Lahmacun', 'price': 45.0, 'desc': 'İnce hamur, özel kıymalı harç',
                     'image': 'food_category.png'},
                    {'name': 'Lahmacun (3\'lü)', 'price': 120.0, 'desc': '3 adet lahmacun',
                     'image': 'food_category.png'},
                ],
                'Salatalar': [
                    {'name': 'Çoban Salata', 'price': 35.0, 'desc': 'Domates, salatalık, biber, soğan',
                     'image': 'th-club.png'},
                    {'name': 'Mevsim Salata', 'price': 40.0, 'desc': 'Mevsim yeşillikleri, nar ekşili sos',
                     'image': 'th-club.png'},
                ],
                'İçecekler': [
                    {'name': 'Ayran', 'price': 12.0, 'desc': '', 'image': 'th-water.png'},
                    {'name': 'Şalgam', 'price': 15.0, 'desc': 'Acılı şalgam suyu', 'image': 'th-fanta.png'},
                ],
            },
            'demo_restaurant_sushi_zen': {
                'Sushi Setleri': [
                    {'name': 'California Roll (8 adet)', 'price': 140.0, 'desc': 'Yengeç, avokado, salatalık',
                     'image': 'th-maki.png',
                     'addons': [
                         ('Sos', 'Ekstra Soya Sosu', 5.0, 'select'),
                         ('Sos', 'Wasabi', 5.0, 'select'),
                         ('Sos', 'Spicy Mayo', 10.0, 'select'),
                     ]},
                    {'name': 'Salmon Roll (8 adet)', 'price': 160.0, 'desc': 'Taze somon, avokado, Philadelphia peynir',
                     'image': 'th-salmon-avocado.png'},
                    {'name': 'Dragon Roll (8 adet)', 'price': 180.0, 'desc': 'Karides tempura, avokado, yılan balığı sosu',
                     'image': 'th-temaki.png'},
                    {'name': 'Sashimi Tabağı', 'price': 220.0, 'desc': 'Somon, ton balığı, hamachi (12 dilim)',
                     'image': 'th-tuna.png'},
                ],
                'Ramen': [
                    {'name': 'Tonkotsu Ramen', 'price': 130.0, 'desc': 'Domuz kemik suyu, chashu, yumurta, nori',
                     'image': 'th-pasta.png'},
                    {'name': 'Miso Ramen', 'price': 120.0, 'desc': 'Miso bazlı, tofu, sebzeler',
                     'image': 'th-pasta.png'},
                ],
                'Başlangıçlar': [
                    {'name': 'Edamame', 'price': 45.0, 'desc': 'Tuzlu soya fasulyesi',
                     'image': 'th-mozza.png'},
                    {'name': 'Gyoza (6 adet)', 'price': 65.0, 'desc': 'Japon mantısı, ponzu sos',
                     'image': 'th-mozza.png'},
                ],
                'İçecekler': [
                    {'name': 'Yeşil Çay', 'price': 25.0, 'desc': 'Japon yeşil çayı', 'image': 'th-green_tea.png'},
                    {'name': 'Sake', 'price': 80.0, 'desc': 'Sıcak sake', 'image': 'th-ice_tea.png'},
                ],
            },
            'demo_restaurant_pizza_napoli': {
                'Pizzalar': [
                    {'name': 'Margherita', 'price': 95.0, 'desc': 'Domates sosu, mozzarella, fesleğen',
                     'image': 'th-pizza-ma.png',
                     'addons': [
                         ('Hamur', 'İnce Hamur', 0.0, 'select'),
                         ('Hamur', 'Kalın Hamur', 0.0, 'select'),
                         ('Ekstra Malzeme', 'Mantar', 10.0, 'quantity'),
                         ('Ekstra Malzeme', 'Zeytin', 10.0, 'quantity'),
                         ('Ekstra Malzeme', 'Sucuk', 15.0, 'quantity'),
                     ]},
                    {'name': 'Pepperoni', 'price': 115.0, 'desc': 'Bol pepperoni, mozzarella',
                     'image': 'th-pizza-fu.png'},
                    {'name': 'Quattro Formaggi', 'price': 125.0, 'desc': 'Mozzarella, gorgonzola, parmesan, ricotta',
                     'image': 'th-pizza-ve.png'},
                    {'name': 'Napoli Special', 'price': 140.0, 'desc': 'Sucuk, mantar, biber, zeytin, mısır, kaşar',
                     'image': 'th-pizza.png'},
                ],
                'Makarnalar': [
                    {'name': 'Spaghetti Bolognese', 'price': 90.0, 'desc': 'Kıymalı domates soslu spagetti',
                     'image': 'th-pasta.png'},
                    {'name': 'Penne Arabiata', 'price': 85.0, 'desc': 'Acılı domates soslu penne',
                     'image': 'th-pasta-4f.png'},
                    {'name': 'Fettuccine Alfredo', 'price': 95.0, 'desc': 'Kremalı parmesan soslu fettuccine',
                     'image': 'th-pasta-4f.png'},
                ],
                'Salatalar': [
                    {'name': 'Caesar Salata', 'price': 65.0, 'desc': 'Marul, parmesan, kruton, Caesar sos',
                     'image': 'th-club.png'},
                ],
                'Tatlılar': [
                    {'name': 'Tiramisu', 'price': 60.0, 'desc': 'İtalyan klasiği tiramisu',
                     'image': 'th-milkshake_banana.png'},
                    {'name': 'Panna Cotta', 'price': 55.0, 'desc': 'Vanilyalı panna cotta, çilek sosu',
                     'image': 'th-milkshake_banana.png'},
                ],
                'İçecekler': [
                    {'name': 'San Pellegrino', 'price': 30.0, 'desc': 'İtalyan maden suyu', 'image': 'th-water.png'},
                    {'name': 'Espresso', 'price': 20.0, 'desc': '', 'image': 'th-espresso.png'},
                ],
            },
            'demo_restaurant_ev_yemekleri': {
                'Ana Yemekler': [
                    {'name': 'Karnıyarık', 'price': 85.0, 'desc': 'Patlıcan, kıyma, domates, biber',
                     'image': 'food_category.png'},
                    {'name': 'İzmir Köfte', 'price': 90.0, 'desc': 'Patatesli köfte, domates soslu',
                     'image': 'food_category.png'},
                    {'name': 'Tavuk Sote', 'price': 80.0, 'desc': 'Sebzeli tavuk sote, pilav ile',
                     'image': 'food_category.png'},
                    {'name': 'Etli Nohut', 'price': 75.0, 'desc': 'Kuşbaşılı nohut yemeği',
                     'image': 'food_category.png'},
                ],
                'Çorbalar': [
                    {'name': 'Mercimek Çorbası', 'price': 35.0, 'desc': 'Kırmızı mercimek çorbası',
                     'image': 'food_category.png'},
                    {'name': 'Ezogelin Çorbası', 'price': 35.0, 'desc': 'Geleneksel ezogelin',
                     'image': 'food_category.png'},
                    {'name': 'İşkembe Çorbası', 'price': 50.0, 'desc': 'Sarımsaklı, sirkeli',
                     'image': 'food_category.png'},
                ],
                'Zeytinyağlılar': [
                    {'name': 'İmam Bayıldı', 'price': 55.0, 'desc': 'Zeytinyağlı patlıcan dolması',
                     'image': 'food_category.png'},
                    {'name': 'Yaprak Sarma', 'price': 50.0, 'desc': 'Zeytinyağlı yaprak sarması',
                     'image': 'food_category.png'},
                    {'name': 'Barbunya Pilaki', 'price': 45.0, 'desc': 'Zeytinyağlı barbunya',
                     'image': 'food_category.png'},
                ],
                'İçecekler': [
                    {'name': 'Ayran', 'price': 10.0, 'desc': 'Ev yapımı ayran', 'image': 'th-water.png'},
                    {'name': 'Komposto', 'price': 15.0, 'desc': 'Mevsim meyveli komposto',
                     'image': 'th-ice_tea.png'},
                ],
            },
        }

    def _get_demo_reviews(self):
        """Restaurant reviews."""
        return {
            'demo_restaurant_burger_house': [
                (5, 5, 'Harika burgerler! Özellikle BBQ Burger muhteşem.'),
                (4, 5, 'Lezzetli ama teslimat biraz geç geldi.'),
                (5, 4, 'Her zaman tercihim, kalite hiç düşmüyor.'),
            ],
            'demo_restaurant_pide_ustasi': [
                (5, 5, 'En iyi pide burada. Karışık pide favorim.'),
                (4, 4, 'Güzel lezzetler, lahmacun çok iyi.'),
            ],
            'demo_restaurant_sushi_zen': [
                (5, 5, 'İstanbul\'un en iyi sushisi!'),
                (4, 5, 'Sashimi çok taze, fiyatlar biraz yüksek ama değer.'),
                (5, 5, 'Dragon Roll muhteşemdi.'),
                (3, 4, 'Ramen daha sıcak gelebilirdi.'),
            ],
            'demo_restaurant_pizza_napoli': [
                (5, 5, 'Gerçek İtalyan pizzası! Margherita harika.'),
                (4, 4, 'Ücretsiz teslimat ve lezzetli pizza, ne istersin!'),
                (5, 5, 'Tiramisu efsane.'),
            ],
            'demo_restaurant_ev_yemekleri': [
                (5, 5, 'Annemin yaptığından farkı yok!'),
                (5, 5, 'Karnıyarık ve mercimek çorbası mükemmel.'),
                (4, 5, 'Ev yemeği özlemi çekenler için birebir.'),
            ],
        }

    def _get_demo_product_reviews(self):
        """Product-level reviews. Maps restaurant xmlid → product name → list of (rating, comment)."""
        return {
            'demo_restaurant_burger_house': {
                'Classic Burger': [(5, 'Mükemmel burger!'), (4, 'Çok lezzetli, soslar harika.')],
                'Cheese Burger': [(5, 'Cheddar peyniri çok iyi erimiş.'), (4, 'Güzel ama biraz yağlı.')],
                'BBQ Burger': [(5, 'BBQ sos efsane!'), (5, 'En sevdiğim burger.')],
                'Tavuk Burger': [(4, 'Tavuk çok çıtır.')],
                'Patates Kızartması': [(5, 'Çıtır çıtır, harika baharat.')],
                'Coca-Cola 330ml': [(4, 'Soğuk geldi, güzel.')],
            },
            'demo_restaurant_pide_ustasi': {
                'Kaşarlı Pide': [(5, 'Peynir bol, hamur çıtır.'), (5, 'Mükemmel!')],
                'Kuşbaşılı Pide': [(4, 'Et yumuşacık.'), (5, 'Harika lezzet.')],
                'Karışık Pide': [(5, 'En iyisi bu!'), (4, 'Doyurucu ve lezzetli.')],
                'Lahmacun': [(5, 'İnce hamur, tam kıvamında.'), (4, 'Güzel ama biraz daha acılı olabilirdi.')],
            },
            'demo_restaurant_sushi_zen': {
                'California Roll (8 adet)': [(5, 'Çok taze!'), (4, 'Güzel sunum.')],
                'Salmon Roll (8 adet)': [(5, 'Somon muhteşem taze.'), (5, 'En iyi roll!')],
                'Dragon Roll (8 adet)': [(5, 'Tempura karides harika.'), (5, 'Görsel şölen.')],
                'Sashimi Tabağı': [(5, 'Balık çok taze.'), (4, 'Porsiyonlar iyi.')],
                'Tonkotsu Ramen': [(4, 'Suyu çok lezzetli.'), (3, 'Biraz soğuk geldi.')],
            },
            'demo_restaurant_pizza_napoli': {
                'Margherita': [(5, 'Tam İtalyan usulü!'), (5, 'Fesleğen taze, hamur harika.'), (4, 'Çok güzel.')],
                'Pepperoni': [(5, 'Pepperoni çok lezzetli.'), (4, 'Güzel pizza.')],
                'Quattro Formaggi': [(5, '4 peynir muhteşem uyum!'), (5, 'Peynir sevenler için birebir.')],
                'Napoli Special': [(4, 'Malzemeler bol.'), (5, 'En doyurucu pizza.')],
                'Spaghetti Bolognese': [(4, 'Klasik ve güzel.'), (5, 'Sos ev yapımı gibi.')],
                'Tiramisu': [(5, 'Efsane tatlı!'), (5, 'İtalya\'da yediğimden farkı yok.')],
            },
            'demo_restaurant_ev_yemekleri': {
                'Karnıyarık': [(5, 'Ev yapımı tadında!'), (5, 'Muhteşem.'), (4, 'Çok güzel ama biraz tuzlu.')],
                'İzmir Köfte': [(5, 'Annemin yaptığı gibi.'), (4, 'Lezzetli.')],
                'Mercimek Çorbası': [(5, 'Tam kıvamında.'), (5, 'Harika!')],
                'İmam Bayıldı': [(5, 'Zeytinyağlıların en iyisi.'), (4, 'Çok güzel.')],
                'Yaprak Sarma': [(5, 'İnce ince sarılmış, mükemmel.'), (5, 'Tadı muhteşem.')],
            },
        }

    def load_demo_data(self):
        IrModelData = self.env['ir.model.data']
        Restaurant = self.env['food.restaurant']
        Category = self.env['product.public.category']
        Product = self.env['product.template']
        Addon = self.env['food.product.addon']
        WorkHour = self.env['food.restaurant.work.hour']
        Review = self.env['food.restaurant.review']
        ProductReview = self.env['food.product.review']

        restaurants_data = self._get_demo_restaurants()
        products_data = self._get_demo_products()
        reviews_data = self._get_demo_reviews()
        product_reviews_data = self._get_demo_product_reviews()

        for rest_data in restaurants_data:
            xmlid = rest_data.pop('xmlid')
            categories_names = rest_data.pop('categories')
            work_hours = rest_data.pop('work_hours')

            # Check if already exists
            existing = IrModelData.search([
                ('module', '=', 'ronix_food_delivery'),
                ('name', '=', xmlid),
            ], limit=1)
            if existing:
                continue

            # Create restaurant
            restaurant = Restaurant.create(rest_data)
            IrModelData.create({
                'module': 'ronix_food_delivery',
                'name': xmlid,
                'model': 'food.restaurant',
                'res_id': restaurant.id,
                'noupdate': True,
            })

            # Create categories and link to restaurant
            cat_map = {}
            for cat_name in categories_names:
                cat_xmlid = f'{xmlid}_cat_{cat_name.lower().replace(" ", "_").replace("ı", "i").replace("ö", "o").replace("ü", "u").replace("ş", "s").replace("ç", "c").replace("ğ", "g")}'
                cat_vals = {'name': cat_name}
                # Add category image
                cat_img_file = CATEGORY_IMAGES.get(cat_name)
                if cat_img_file:
                    cat_img = _load_image(cat_img_file)
                    if cat_img:
                        cat_vals['image_1920'] = cat_img
                category = Category.create(cat_vals)
                IrModelData.create({
                    'module': 'ronix_food_delivery',
                    'name': cat_xmlid,
                    'model': 'product.public.category',
                    'res_id': category.id,
                    'noupdate': True,
                })
                cat_map[cat_name] = category
                restaurant.write({'category_ids': [(4, category.id)]})

            # Create work hours
            for day, start, end in work_hours:
                wh = WorkHour.create({
                    'restaurant_id': restaurant.id,
                    'day_of_week': day,
                    'start_time': start,
                    'end_time': end,
                })
                IrModelData.create({
                    'module': 'ronix_food_delivery',
                    'name': f'{xmlid}_wh_{day}_{int(start)}',
                    'model': 'food.restaurant.work.hour',
                    'res_id': wh.id,
                    'noupdate': True,
                })

            # Create products
            rest_products = products_data.get(xmlid, {})
            rest_product_reviews = product_reviews_data.get(xmlid, {})
            for cat_name, items in rest_products.items():
                category = cat_map.get(cat_name)
                if not category:
                    continue

                for item in items:
                    addons_data = item.pop('addons', [])
                    image_file = item.pop('image', None)
                    prod_xmlid = f'{xmlid}_prod_{item["name"].lower().replace(" ", "_")[:30]}'

                    product_vals = {
                        'name': item['name'],
                        'list_price': item['price'],
                        'description_sale': item.get('desc', ''),
                        'is_food': True,
                        'food_restaurant_id': restaurant.id,
                        'type': 'consu',
                        'sale_ok': True,
                        'is_published': True,
                        'public_categ_ids': [(4, category.id)],
                    }
                    if image_file:
                        img_data = _load_image(image_file)
                        if img_data:
                            product_vals['image_1920'] = img_data

                    product = Product.create(product_vals)
                    IrModelData.create({
                        'module': 'ronix_food_delivery',
                        'name': prod_xmlid,
                        'model': 'product.template',
                        'res_id': product.id,
                        'noupdate': True,
                    })

                    # Create addons
                    for idx, (group, name, price, sel_type) in enumerate(addons_data):
                        addon = Addon.create({
                            'product_id': product.id,
                            'group_name': group,
                            'name': name,
                            'extra_price': price,
                            'selection_type': sel_type,
                            'sequence': (idx + 1) * 10,
                        })
                        IrModelData.create({
                            'module': 'ronix_food_delivery',
                            'name': f'{prod_xmlid}_addon_{idx}',
                            'model': 'food.product.addon',
                            'res_id': addon.id,
                            'noupdate': True,
                        })

                    # Create product reviews
                    prod_reviews = rest_product_reviews.get(item['name'], [])
                    for ridx, (rating, comment) in enumerate(prod_reviews):
                        prev = ProductReview.create({
                            'product_id': product.id,
                            'user_id': self.env.user.id,
                            'rating': rating,
                            'comment': comment,
                        })
                        IrModelData.create({
                            'module': 'ronix_food_delivery',
                            'name': f'{prod_xmlid}_prevw_{ridx}',
                            'model': 'food.product.review',
                            'res_id': prev.id,
                            'noupdate': True,
                        })

            # Create restaurant reviews
            rest_reviews = reviews_data.get(xmlid, [])
            for idx, (rating, food_rating, comment) in enumerate(rest_reviews):
                review = Review.create({
                    'restaurant_id': restaurant.id,
                    'user_id': self.env.user.id,
                    'rating': rating,
                    'food_rating': food_rating,
                    'comment': comment,
                })
                IrModelData.create({
                    'module': 'ronix_food_delivery',
                    'name': f'{xmlid}_review_{idx}',
                    'model': 'food.restaurant.review',
                    'res_id': review.id,
                    'noupdate': True,
                })

    def unload_demo_data(self):
        IrModelData = self.env['ir.model.data']

        # Delete in correct order (children first) to avoid FK constraint errors
        delete_order = [
            'food.product.review',
            'food.restaurant.review',
            'food.product.addon',
            'food.restaurant.work.hour',
            'product.template',
            'product.public.category',
            'food.restaurant',
        ]

        for model_name in delete_order:
            # Fresh search each iteration to avoid stale recordset references
            refs = IrModelData.search([
                ('module', '=', 'ronix_food_delivery'),
                ('name', 'like', 'demo_%'),
                ('model', '=', model_name),
            ])
            for ref in refs:
                try:
                    record = self.env[model_name].browse(ref.res_id)
                    if record.exists():
                        record.unlink()
                except Exception:
                    pass
            refs.unlink()

        # Clean up any remaining demo refs
        remaining = IrModelData.search([
            ('module', '=', 'ronix_food_delivery'),
            ('name', 'like', 'demo_%'),
        ])
        for ref in remaining:
            try:
                record = self.env[ref.model].browse(ref.res_id)
                if record.exists():
                    record.unlink()
            except Exception:
                pass
        remaining.unlink()
