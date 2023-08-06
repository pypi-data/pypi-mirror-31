//
//  TabBarRouter.swift
//
//  Created by Bohdan Ivanov on 6.05.18.
//  Copyright © 2018 bivanov. All rights reserved.
//

import Foundation

import UIKit

class TabBarRouter: AbstractRouter {
    var routers: [AbstractRouter]

    init(routers: AbstractRouter...) {
        self.routers = routers
    }
    
    func setup() -> UIViewController {
        let tabBarController = ViperTabBarController()
        var viewControllers = [UIViewController]()
        
        for router in self.routers {
            viewControllers.append(router.setup())
        }

        tabBarController.viewControllers = viewControllers
        
        return tabBarController
    }
}
