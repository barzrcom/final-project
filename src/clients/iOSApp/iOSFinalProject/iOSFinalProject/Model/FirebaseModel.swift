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

class Firebase{
    var ref: DatabaseReference!

    init() {
        FirebaseApp.configure()
        ref = Database.database().reference()
    }
}
