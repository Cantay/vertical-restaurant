/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";

function escapeHtml(value) {
    return $('<div>').text(value || '').html();
}

function renderStars(rating) {
    var html = '';
    for (var i = 1; i <= 5; i++) {
        html += '<i class="ri-star-fill ' + (i <= rating ? 'text-warning' : 'text-secondary opacity-25') + '" style="font-size:0.65rem;"></i>';
    }
    return html;
}

function renderReviewCard(review) {
    var tagsHtml = '';
    if (review.tags && review.tags.length) {
        tagsHtml = '<div class="d-flex flex-wrap gap-1 mt-2">' + review.tags.map(function (tag) {
            return '<span class="badge bg-light text-secondary border-0" style="font-size:0.6rem; font-weight:500;">' + escapeHtml(tag) + '</span>';
        }).join('') + '</div>';
    }

    return '' +
        '<div class="pb-3 border-bottom border-light border-dashed last-child-border-0">' +
            '<div class="d-flex align-items-center justify-content-between mb-1">' +
                '<div class="d-flex align-items-center gap-2">' +
                    '<div class="bg-light rounded-circle d-flex align-items-center justify-content-center" style="width:1.5rem; height:1.5rem;">' +
                        '<i class="ri-user-line text-secondary" style="font-size:0.75rem;"></i>' +
                    '</div>' +
                    '<span class="fw-bold text-dark" style="font-size:0.75rem;">' + escapeHtml(review.author) + '</span>' +
                '</div>' +
                '<span class="text-secondary" style="font-size:0.65rem;">' + escapeHtml(review.date) + '</span>' +
            '</div>' +
            '<div class="d-flex align-items-center gap-1 mb-2">' + renderStars(review.rating) + '</div>' +
            '<p class="text-dark mb-0" style="font-size:0.75rem; line-height:1.4;">' + escapeHtml(review.comment || _t('Yorum yok.')) + '</p>' +
            tagsHtml +
        '</div>';
}

function loadReviewFeed($feed, reset) {
    if (!$feed.length || $feed.data('loading')) {
        return;
    }

    var offset = reset ? 0 : ($feed.data('offset') || 0);
    var pageSize = parseInt($feed.data('page-size'), 10) || 20;
    var rating = $feed.data('rating');
    var $list = $feed.find('.js-review-list');
    var $loading = $feed.find('.js-review-loading');
    var $empty = $feed.find('.js-review-empty');

    $feed.data('loading', true);
    $loading.removeClass('d-none');

    rpc('/food/reviews', {
        review_type: $feed.data('review-type'),
        record_id: $feed.data('record-id'),
        offset: offset,
        limit: pageSize,
        rating: rating || false,
    }).then(function (result) {
        result = result || {};
        var reviews = result.reviews || [];

        if (reset) {
            $list.empty();
        }

        if (!reviews.length && offset === 0) {
            $empty.removeClass('d-none');
        } else {
            $empty.addClass('d-none');
        }

        if (reviews.length) {
            $list.append(reviews.map(renderReviewCard).join(''));
        }

        $feed.data('offset', offset + reviews.length);
        $feed.data('has_more', !!result.has_more);
    }).catch(function () {
        if (reset) {
            $list.empty();
            $empty.removeClass('d-none').text(_t('Yorumlar yuklenemedi.'));
        }
        $feed.data('has_more', false);
    }).finally(function () {
        $feed.data('loading', false);
        $loading.addClass('d-none');
    });
}

function setupReviewFeed($feed) {
    if (!$feed.length || $feed.data('initialized')) {
        return;
    }

    $feed.data({
        initialized: true,
        offset: 0,
        rating: '',
        loading: false,
        has_more: true,
    });

    var sentinel = $feed.find('.js-review-sentinel').get(0);
    if (sentinel && 'IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting && $feed.data('has_more')) {
                    loadReviewFeed($feed, false);
                }
            });
        }, {
            root: null,
            threshold: 0.1,
        });
        observer.observe(sentinel);
        $feed.data('observer', observer);
    }

    loadReviewFeed($feed, true);
}

$(document).ready(function () {
    $('.js-review-feed').each(function () {
        setupReviewFeed($(this));
    });

    // Star Rating Logic
    $(document).on('click', '.star-icon', function () {
        var $star = $(this);
        var $container = $star.closest('.star-rating');
        var value = $star.data('value');

        // Update stars UI
        $container.find('.star-icon').each(function () {
            var starVal = $(this).data('value');
            if (starVal <= value) {
                $(this).removeClass('ri-star-line text-secondary').addClass('ri-star-fill text-warning');
            } else {
                $(this).removeClass('ri-star-fill text-warning').addClass('ri-star-line text-secondary');
            }
        });

        // Update hidden input
        $container.find('input').val(value);

        checkFormValidity($container.closest('.offcanvas'));
    });

    // Tag Selection Logic
    $(document).on('click', '.review-tag-btn', function () {
        $(this).toggleClass('food-bg-orange text-white border-orange shadow-sm');
        $(this).toggleClass('btn-light text-dark');
    });

    // Form Submission
    $(document).on('click', '.btn-submit-review', function () {
        var $btn = $(this);
        if ($btn.hasClass('disabled')) return;

        var $canvas = $btn.closest('.offcanvas');
        var orderId = $canvas.data('order-id');

        var payload = {
            order_id: orderId,
            restaurant_rating: $canvas.find('input[name="restaurant_rating"]').val(),
            food_rating: $canvas.find('input[name="food_rating"]').val(),
            restaurant_tags: getSelectedTags($canvas.find('.tag-container[data-type="restaurant"]')),
            food_tags: getSelectedTags($canvas.find('.tag-container[data-type="food"]')),
        };

        $btn.addClass('disabled').html('<i class="ri-loader-4-line ri-spin"></i> Gönderiliyor...');

        rpc('/food/order/review/save', payload).then(function (result) {
            if (result.status === 'success') {
                // Update button in orders page
                $canvas.offcanvas('hide');
                location.reload(); // Refresh to update UI
            } else {
                alert(result.message || 'Bir hata oluştu.');
                $btn.removeClass('disabled').html('<i class="ri-send-plane-fill"></i> Değerlendirmeyi Gönder');
            }
        });
    });

    $(document).on('click', '.js-review-filter', function () {
        var $btn = $(this);
        var $wrapper = $btn.closest('.js-review-filters');
        var $feed = $wrapper.nextAll('.js-review-feed').first();

        $wrapper.find('.js-review-filter')
            .removeClass('food-bg-orange text-white active')
            .addClass('btn-light text-dark');

        $btn.addClass('food-bg-orange text-white active')
            .removeClass('btn-light text-dark');

        $feed.data('rating', $btn.data('rating') || '');
        $feed.data('offset', 0);
        $feed.data('has_more', true);
        loadReviewFeed($feed, true);
    });

    $(document).on('shown.bs.offcanvas', '#foodDetailOffcanvas', function () {
        $(this).find('.js-review-feed').each(function () {
            setupReviewFeed($(this));
        });
    });

    function getSelectedTags($container) {
        var tags = [];
        $container.find('.review-tag-btn.food-bg-orange').each(function () {
            tags.push($(this).data('tag-id'));
        });
        return tags;
    }

    function checkFormValidity($canvas) {
        var resRating = $canvas.find('input[name="restaurant_rating"]').val();
        var foodRating = $canvas.find('input[name="food_rating"]').val();
        var $submitBtn = $canvas.find('.btn-submit-review');

        if (parseInt(resRating) > 0 && parseInt(foodRating) > 0) {
            $submitBtn.removeClass('disabled');
        } else {
            $submitBtn.addClass('disabled');
        }
    }
});
