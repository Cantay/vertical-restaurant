# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Ronix Çevrimiçi Form Yönetimi',
    'version': '18.0.1.0.0',
    'category': 'Operations',
    'summary': 'Lokasyon bazlı dinamik çevrimiçi form tasarımı, yayınlama ve gönderim yönetimi',
    'description': """Lokasyon bazlı çevrimiçi formlar oluşturur, yayınlar ve gönderimleri backend tarafında yönetir.
Kalite yönetimi lokasyonlarıyla entegre çalışarak her lokasyona özel form linkleri üretir.
Metin, sayı, tarih, tarih-saat, seçim ve onay gibi farklı alan tiplerini destekler.
Zorunlu alan, yardım metni, placeholder, kolon genişliği ve seçim seçenekleri tanımlar.
Public frontend form sayfaları, gönderim endpointleri ve backend gönderim takibi sağlar.
Takvim rengi, takvim tarihi, durum, not ve PDF çıktısı desteği sunar.""",
    'author': 'Odoo Custom',
    'depends': [
        'base',
        'website',
        'ronix_quality_manager',
    ],
    'data': [
        'security/ronix_online_form_security.xml',
        'security/ir.model.access.csv',
        'views/ronix_online_form_views.xml',
        'views/ronix_online_form_submission_views.xml',
        'views/menus.xml',
        'views/ronix_online_form_templates.xml',
        'report/ronix_online_form_submission_report.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ronix_online_form_manager/static/src/scss/ronix_online_form.scss',
            'ronix_online_form_manager/static/src/js/ronix_online_form_designer.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
