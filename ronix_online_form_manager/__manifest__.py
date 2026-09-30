# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Ronix Çevrimiçi Form Yönetimi',
    'version': '18.0.1.0.0',
    'category': 'Operations',
    'summary': 'Lokasyon bazlı dinamik çevrimiçi form tasarımı, yayınlama ve gönderim yönetimi',
    'description': """
Ronix Çevrimiçi Form Yönetimi
=============================

Bu modül, lokasyon bazlı çevrimiçi formlar oluşturmayı, website üzerinden
yayınlamayı ve gelen gönderimleri backend tarafında yetki kontrollü şekilde
yönetmeyi sağlar. Kalite yönetimi lokasyonlarıyla entegre çalışarak her
lokasyona özel form linkleri, alan yapıları ve gönderim kayıtları üretir.

Öne çıkan özellikler:

* Lokasyon bazlı form şablonları ve kısa URL üretimi.
* Metin, sayı, tarih, tarih-saat, seçim ve onay gibi farklı alan tipleri.
* Zorunlu alan, yardım metni, placeholder, kolon genişliği ve seçim seçenekleri
  yönetimi.
* Formları taslak/yayında durumlarıyla yönetme ve arşivleme.
* Public frontend form sayfaları ve gönderim endpointleri.
* Gelen gönderimleri alan değerleriyle birlikte backend tarafında izleme.
* Takvim rengi, takvim tarihi, durum, not ve PDF çıktısı desteği.
* Form yerleşimini frontend tasarım aracıyla kaydetme altyapısı.
    """,
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
