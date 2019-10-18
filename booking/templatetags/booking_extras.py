from django import template
register = template.Library()


@register.filter(name='times')
def times(number):
    return range(number)


@register.filter
def index(listt, i):
    return listt[int(i)]


@register.filter
def index2(listt, i):
    return listt[i]

@register.filter
def multiply(value, arg):
    return value*arg
