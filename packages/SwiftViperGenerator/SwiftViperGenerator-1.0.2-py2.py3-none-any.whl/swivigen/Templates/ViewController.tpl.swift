{% extends "Header.tpl.swift" %}
{% block content %}
import UIKit

class {{ module_name }}Controller: ViperController<{{ module_name }}Presenter>,
    {{ module_name }}View {

    override func viewDidLoad() {
        super.viewDidLoad()
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
    }
}
{% endblock %}
