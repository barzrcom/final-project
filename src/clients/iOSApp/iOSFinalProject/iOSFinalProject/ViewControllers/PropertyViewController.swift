//
//  PropertyViewController.swift
//  iOSFinalProject
//
//  Created by Eti Negev on 05/12/2018.
//  Copyright © 2018 Eti Negev. All rights reserved.
//

import UIKit

class PropertyViewController: UIViewController {

    @IBOutlet weak var addressLabel: UILabel!
    var propertyId:Int?
    var property:Property?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        if property != nil {
            title = property?.address
            addressLabel.text = property?.address
        }
    }
    
}
