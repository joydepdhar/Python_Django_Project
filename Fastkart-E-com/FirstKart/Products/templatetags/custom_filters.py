# your_app/templatetags/custom_filters.py

from django import template

register = template.Library()
@register.filter(name='get_item')
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(str(key), 0)
    return 0

# @register.filter(name='get_rating_percentage')
# def get_rating_percentage(rating, rating_counts):
#     # Check if rating_counts is a valid dictionary
#     if not isinstance(rating_counts, dict):
#         return 0  # Return 0 if invalid input

#     total_reviews = sum(rating_counts.values())
#     if total_reviews == 0:
#         return 0
#     return (rating_counts.get(str(rating), 0) / total_reviews) * 100
