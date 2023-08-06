{% extends "Header.tpl.swift" %}
{% block content %}
protocol {{ module_name }}View: class {
    var presenter: {{ module_name }}Presenter! { get }
}
{% endblock %}
