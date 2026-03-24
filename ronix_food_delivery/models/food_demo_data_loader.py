from odoo import models

DEMO_XMLID_PREFIX = 'ronix_food_delivery.demo_'


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
                'always_open': False,
                'is_popular': True,
                'is_fast_delivery': True,
                'delivery_fee': 15.0,
                'delivery_time_min': 20,
                'delivery_time_max': 35,
                'min_order_amount': 80.0,
                'platform_commission_rate': 15.0,
                'categories': ['Burgerler', 'Yan Ürünler', 'İçecekler', 'Tatlılar'],
                'work_hours': [
                    ('0', 10.0, 23.0), ('1', 10.0, 23.0), ('2', 10.0, 23.0),
                    ('3', 10.0, 23.0), ('4', 10.0, 24.0), ('5', 11.0, 24.0),
                    ('6', 11.0, 22.0),
                ],
            },
            {
                'xmlid': 'demo_restaurant_pide_ustasi',
                'name': 'Pide Ustası',
                'description': 'Karadeniz usulü pide ve lahmacun. Odun fırınında pişen geleneksel lezzetler.',
                'phone': '+90 212 555 0202',
                'address': 'Kadıköy, Moda Caddesi No:18, İstanbul',
                'always_open': False,
                'is_popular': True,
                'delivery_fee': 10.0,
                'delivery_time_min': 25,
                'delivery_time_max': 40,
                'min_order_amount': 60.0,
                'platform_commission_rate': 12.0,
                'categories': ['Pideler', 'Lahmacunlar', 'Salatalar', 'İçecekler'],
                'work_hours': [
                    ('0', 11.0, 22.0), ('1', 11.0, 22.0), ('2', 11.0, 22.0),
                    ('3', 11.0, 22.0), ('4', 11.0, 23.0), ('5', 11.0, 23.0),
                    ('6', 12.0, 21.0),
                ],
            },
            {
                'xmlid': 'demo_restaurant_sushi_zen',
                'name': 'Sushi Zen',
                'description': 'Taze malzemelerle hazırlanan otantik Japon mutfağı. Sushi, sashimi ve ramen.',
                'phone': '+90 212 555 0303',
                'address': 'Beşiktaş, Barbaros Bulvarı No:55, İstanbul',
                'always_open': False,
                'is_fast_delivery': True,
                'delivery_fee': 20.0,
                'delivery_time_min': 30,
                'delivery_time_max': 45,
                'min_order_amount': 120.0,
                'platform_commission_rate': 18.0,
                'categories': ['Sushi Setleri', 'Ramen', 'Başlangıçlar', 'İçecekler'],
                'work_hours': [
                    ('0', 12.0, 22.0), ('1', 12.0, 22.0), ('2', 12.0, 22.0),
                    ('3', 12.0, 22.0), ('4', 12.0, 23.0), ('5', 12.0, 23.0),
                    ('6', 12.0, 21.0),
                ],
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
                'categories': ['Pizzalar', 'Makarnalar', 'Salatalar', 'Tatlılar', 'İçecekler'],
                'work_hours': [],
            },
            {
                'xmlid': 'demo_restaurant_ev_yemekleri',
                'name': 'Annemin Mutfağı',
                'description': 'Ev yapımı Türk mutfağı. Günlük taze pişen yemekler, çorbalar ve zeytinyağlılar.',
                'phone': '+90 212 555 0505',
                'address': 'Üsküdar, Bağlarbaşı Caddesi No:7, İstanbul',
                'always_open': False,
                'is_popular': True,
                'delivery_fee': 5.0,
                'delivery_time_min': 25,
                'delivery_time_max': 40,
                'min_order_amount': 50.0,
                'platform_commission_rate': 10.0,
                'categories': ['Ana Yemekler', 'Çorbalar', 'Zeytinyağlılar', 'İçecekler'],
                'work_hours': [
                    ('0', 10.0, 21.0), ('1', 10.0, 21.0), ('2', 10.0, 21.0),
                    ('3', 10.0, 21.0), ('4', 10.0, 21.0), ('5', 10.0, 21.0),
                ],
            },
        ]

    def _get_demo_products(self):
        return {
            'demo_restaurant_burger_house': {
                'Burgerler': [
                    {'name': 'Classic Burger', 'price': 120.0, 'desc': 'Dana köfte, marul, domates, turşu, özel sos',
                     'addons': [
                         ('Ek Malzeme', 'Ekstra Peynir', 15.0, 'select'),
                         ('Ek Malzeme', 'Bacon', 20.0, 'select'),
                         ('Ek Malzeme', 'Jalapeno', 10.0, 'select'),
                         ('Burger Boyutu', 'Double Köfte', 40.0, 'select'),
                     ]},
                    {'name': 'Cheese Burger', 'price': 135.0, 'desc': 'Dana köfte, çift cheddar, karamelize soğan'},
                    {'name': 'BBQ Burger', 'price': 145.0, 'desc': 'Dana köfte, BBQ sos, çıtır soğan halkası, bacon'},
                    {'name': 'Tavuk Burger', 'price': 110.0, 'desc': 'Çıtır tavuk, marul, mayo, turşu'},
                ],
                'Yan Ürünler': [
                    {'name': 'Patates Kızartması', 'price': 40.0, 'desc': 'Çıtır patates, özel baharat'},
                    {'name': 'Soğan Halkası', 'price': 45.0, 'desc': 'Çıtır pane soğan halkaları'},
                    {'name': 'Nugget (6 adet)', 'price': 55.0, 'desc': 'Tavuk nugget, ranch sos'},
                ],
                'İçecekler': [
                    {'name': 'Coca-Cola 330ml', 'price': 25.0, 'desc': ''},
                    {'name': 'Ayran', 'price': 15.0, 'desc': 'Ev yapımı ayran'},
                    {'name': 'Limonata', 'price': 30.0, 'desc': 'Taze sıkılmış limonata'},
                ],
                'Tatlılar': [
                    {'name': 'Brownie', 'price': 50.0, 'desc': 'Çikolatalı brownie, dondurma ile'},
                ],
            },
            'demo_restaurant_pide_ustasi': {
                'Pideler': [
                    {'name': 'Kaşarlı Pide', 'price': 90.0, 'desc': 'Bol kaşar peynirli, tereyağlı',
                     'addons': [
                         ('Ekstra', 'Yumurta', 10.0, 'select'),
                         ('Ekstra', 'Sucuk', 15.0, 'select'),
                         ('Ekstra', 'Pastırma', 20.0, 'select'),
                     ]},
                    {'name': 'Kuşbaşılı Pide', 'price': 130.0, 'desc': 'Dana kuşbaşı, biber, domates'},
                    {'name': 'Karışık Pide', 'price': 140.0, 'desc': 'Kuşbaşı, kaşar, biber, domates, yumurta'},
                    {'name': 'Sucuklu Pide', 'price': 110.0, 'desc': 'Sucuk, kaşar, yumurta'},
                ],
                'Lahmacunlar': [
                    {'name': 'Lahmacun', 'price': 45.0, 'desc': 'İnce hamur, özel kıymalı harç'},
                    {'name': 'Lahmacun (3\'lü)', 'price': 120.0, 'desc': '3 adet lahmacun'},
                ],
                'Salatalar': [
                    {'name': 'Çoban Salata', 'price': 35.0, 'desc': 'Domates, salatalık, biber, soğan'},
                    {'name': 'Mevsim Salata', 'price': 40.0, 'desc': 'Mevsim yeşillikleri, nar ekşili sos'},
                ],
                'İçecekler': [
                    {'name': 'Ayran', 'price': 12.0, 'desc': ''},
                    {'name': 'Şalgam', 'price': 15.0, 'desc': 'Acılı şalgam suyu'},
                ],
            },
            'demo_restaurant_sushi_zen': {
                'Sushi Setleri': [
                    {'name': 'California Roll (8 adet)', 'price': 140.0, 'desc': 'Yengeç, avokado, salatalık',
                     'addons': [
                         ('Sos', 'Ekstra Soya Sosu', 5.0, 'select'),
                         ('Sos', 'Wasabi', 5.0, 'select'),
                         ('Sos', 'Spicy Mayo', 10.0, 'select'),
                     ]},
                    {'name': 'Salmon Roll (8 adet)', 'price': 160.0, 'desc': 'Taze somon, avokado, Philadelphia peynir'},
                    {'name': 'Dragon Roll (8 adet)', 'price': 180.0, 'desc': 'Karides tempura, avokado, yılan balığı sosu'},
                    {'name': 'Sashimi Tabağı', 'price': 220.0, 'desc': 'Somon, ton balığı, hamachi (12 dilim)'},
                ],
                'Ramen': [
                    {'name': 'Tonkotsu Ramen', 'price': 130.0, 'desc': 'Domuz kemik suyu, chashu, yumurta, nori'},
                    {'name': 'Miso Ramen', 'price': 120.0, 'desc': 'Miso bazlı, tofu, sebzeler'},
                ],
                'Başlangıçlar': [
                    {'name': 'Edamame', 'price': 45.0, 'desc': 'Tuzlu soya fasulyesi'},
                    {'name': 'Gyoza (6 adet)', 'price': 65.0, 'desc': 'Japon mantısı, ponzu sos'},
                ],
                'İçecekler': [
                    {'name': 'Yeşil Çay', 'price': 25.0, 'desc': 'Japon yeşil çayı'},
                    {'name': 'Sake', 'price': 80.0, 'desc': 'Sıcak sake'},
                ],
            },
            'demo_restaurant_pizza_napoli': {
                'Pizzalar': [
                    {'name': 'Margherita', 'price': 95.0, 'desc': 'Domates sosu, mozzarella, fesleğen',
                     'addons': [
                         ('Hamur', 'İnce Hamur', 0.0, 'select'),
                         ('Hamur', 'Kalın Hamur', 0.0, 'select'),
                         ('Ekstra Malzeme', 'Mantar', 10.0, 'quantity'),
                         ('Ekstra Malzeme', 'Zeytin', 10.0, 'quantity'),
                         ('Ekstra Malzeme', 'Sucuk', 15.0, 'quantity'),
                     ]},
                    {'name': 'Pepperoni', 'price': 115.0, 'desc': 'Bol pepperoni, mozzarella'},
                    {'name': 'Quattro Formaggi', 'price': 125.0, 'desc': 'Mozzarella, gorgonzola, parmesan, ricotta'},
                    {'name': 'Napoli Special', 'price': 140.0, 'desc': 'Sucuk, mantar, biber, zeytin, mısır, kaşar'},
                ],
                'Makarnalar': [
                    {'name': 'Spaghetti Bolognese', 'price': 90.0, 'desc': 'Kıymalı domates soslu spagetti'},
                    {'name': 'Penne Arabiata', 'price': 85.0, 'desc': 'Acılı domates soslu penne'},
                    {'name': 'Fettuccine Alfredo', 'price': 95.0, 'desc': 'Kremalı parmesan soslu fettuccine'},
                ],
                'Salatalar': [
                    {'name': 'Caesar Salata', 'price': 65.0, 'desc': 'Marul, parmesan, kruton, Caesar sos'},
                ],
                'Tatlılar': [
                    {'name': 'Tiramisu', 'price': 60.0, 'desc': 'İtalyan klasiği tiramisu'},
                    {'name': 'Panna Cotta', 'price': 55.0, 'desc': 'Vanilyalı panna cotta, çilek sosu'},
                ],
                'İçecekler': [
                    {'name': 'San Pellegrino', 'price': 30.0, 'desc': 'İtalyan maden suyu'},
                    {'name': 'Espresso', 'price': 20.0, 'desc': ''},
                ],
            },
            'demo_restaurant_ev_yemekleri': {
                'Ana Yemekler': [
                    {'name': 'Karnıyarık', 'price': 85.0, 'desc': 'Patlıcan, kıyma, domates, biber'},
                    {'name': 'İzmir Köfte', 'price': 90.0, 'desc': 'Patatesli köfte, domates soslu'},
                    {'name': 'Tavuk Sote', 'price': 80.0, 'desc': 'Sebzeli tavuk sote, pilav ile'},
                    {'name': 'Etli Nohut', 'price': 75.0, 'desc': 'Kuşbaşılı nohut yemeği'},
                ],
                'Çorbalar': [
                    {'name': 'Mercimek Çorbası', 'price': 35.0, 'desc': 'Kırmızı mercimek çorbası'},
                    {'name': 'Ezogelin Çorbası', 'price': 35.0, 'desc': 'Geleneksel ezogelin'},
                    {'name': 'İşkembe Çorbası', 'price': 50.0, 'desc': 'Sarımsaklı, sirkeli'},
                ],
                'Zeytinyağlılar': [
                    {'name': 'İmam Bayıldı', 'price': 55.0, 'desc': 'Zeytinyağlı patlıcan dolması'},
                    {'name': 'Yaprak Sarma', 'price': 50.0, 'desc': 'Zeytinyağlı yaprak sarması'},
                    {'name': 'Barbunya Pilaki', 'price': 45.0, 'desc': 'Zeytinyağlı barbunya'},
                ],
                'İçecekler': [
                    {'name': 'Ayran', 'price': 10.0, 'desc': 'Ev yapımı ayran'},
                    {'name': 'Komposto', 'price': 15.0, 'desc': 'Mevsim meyveli komposto'},
                ],
            },
        }

    def _get_demo_reviews(self):
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

    def load_demo_data(self):
        IrModelData = self.env['ir.model.data']
        Restaurant = self.env['food.restaurant']
        Category = self.env['product.public.category']
        Product = self.env['product.template']
        Addon = self.env['food.product.addon']
        WorkHour = self.env['food.restaurant.work.hour']
        Review = self.env['food.restaurant.review']

        restaurants_data = self._get_demo_restaurants()
        products_data = self._get_demo_products()
        reviews_data = self._get_demo_reviews()

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
                category = Category.create({'name': cat_name})
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
            for cat_name, items in rest_products.items():
                category = cat_map.get(cat_name)
                if not category:
                    continue

                for item in items:
                    addons_data = item.pop('addons', [])
                    prod_xmlid = f'{xmlid}_prod_{item["name"].lower().replace(" ", "_")[:30]}'

                    product = Product.create({
                        'name': item['name'],
                        'list_price': item['price'],
                        'description_sale': item.get('desc', ''),
                        'is_food': True,
                        'food_restaurant_id': restaurant.id,
                        'type': 'consu',
                        'sale_ok': True,
                        'public_categ_ids': [(4, category.id)],
                    })
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

            # Create reviews
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

        # Find all demo records created by us
        demo_refs = IrModelData.search([
            ('module', '=', 'ronix_food_delivery'),
            ('name', 'like', 'demo_%'),
        ])

        # Group by model and delete in correct order (children first)
        delete_order = [
            'food.restaurant.review',
            'food.product.addon',
            'food.restaurant.work.hour',
            'product.template',
            'product.public.category',
            'food.restaurant',
        ]

        for model_name in delete_order:
            refs = demo_refs.filtered(lambda r: r.model == model_name)
            for ref in refs:
                record = self.env[model_name].browse(ref.res_id)
                if record.exists():
                    record.unlink()
            refs.unlink()

        # Clean up any remaining refs
        remaining = demo_refs.filtered(lambda r: r.model not in delete_order)
        for ref in remaining:
            try:
                record = self.env[ref.model].browse(ref.res_id)
                if record.exists():
                    record.unlink()
            except Exception:
                pass
            ref.unlink()
