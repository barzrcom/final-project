//
//  Model.swift
//  iOSFinalProject
//
//  Created by Eti Negev on 05/12/2018.
//  Copyright © 2018 Eti Negev. All rights reserved.
//

import Foundation

class Model{

    static let instance:Model = Model()

    var modelFirebase = FirebaseModel()
    
    
    func getAllProperties(callback: @escaping ([Property]) -> Void){
        modelFirebase.getAllProperties(callback: callback)
    }

}
