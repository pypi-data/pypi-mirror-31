{% extends "Header.tpl.swift" %}
{% block content %}
class {{ module_name }}Presenter: AbstractPresenter {
    var interactor: {{ module_name }}Interactor!
    var router: {{ module_name }}Router!
    weak var view: {{ module_name }}View!
}
{% endblock %}
