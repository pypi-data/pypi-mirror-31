{% extends "Header.tpl.swift" %}
{% block content %}
import UIKit

class {{ module_name }}Router: AbstractRouter {
    weak var view: UIViewController!
    
    static func setup() -> UIViewController {
        let viewController = (UIStoryboard(name: "Main",
                                           bundle: Bundle.main)
                                .instantiateViewController(withIdentifier: "{{ module_name }}Controller") as? {{ module_name }}Controller)!
        
        let presenter = {{ module_name }}Presenter()
        let router = {{ module_name }}Router()
        let interactor = {{ module_name }}Interactor()
        
        viewController.presenter = presenter
        presenter.interactor = interactor
        presenter.view = viewController
        presenter.router = router
        router.view = viewController
        
        return viewController
    }
}

{% endblock %}
