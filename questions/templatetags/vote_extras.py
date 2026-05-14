from django import template

register = template.Library()


@register.filter
def get_vote(votes_dict, answer_id):
    if not votes_dict:
        return None
    return votes_dict.get(answer_id)
