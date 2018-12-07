//
//  FirebaseModel.swift
//  iOSFinalProject
//
//  Created by Eti Negev on 05/12/2018.
//  Copyright © 2018 Eti Negev. All rights reserved.
//

import Foundation
import Firebase
import FirebaseDatabase

class FirebaseModel{
    var ref: DatabaseReference!

    init() {
        FirebaseApp.configure()
        ref = Database.database().reference()
    }
    
    func getAllProperties(callback: @escaping ([Property]) -> Void){
        //Temp hardcoded data
        var data = [Property]()
        data.append(Property(_id:1, _address: "Address 1, Tel Aviv"))
        data.append(Property(_id:2, _address: "Address 2, Tel Aviv"))
        data.append(Property(_id:3, _address: "Address 3, Tel Aviv"))
        data.append(Property(_id:4, _address: "Address 4, Tel Aviv"))
        callback(data)
        
//        ref.child("properties").observe(DataEventType.value, with: { (snapshot) in
//            // Get user value
//            var students = [Property]()
//            let value = snapshot.value as? [String: Any]
//            if value != nil  {
//                for (_, json) in value!{
//                    students.append(Property(json: json as! [String : Any]))
//                }
//            }
//            callback(students)
//        }) { (error) in
//            print(error.localizedDescription)
//        }
    }
}
