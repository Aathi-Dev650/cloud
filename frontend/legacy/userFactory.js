var app = angular.module("cropCureApp", []);


app.factory("userFactory", function(){

    var userData = {};


    return {

        saveUser:function(user){

            userData = user;

        },


        getUser:function(){

            return userData;

        }

    };

});