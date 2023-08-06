if (!RedactorPlugins) var RedactorPlugins = {};
     
RedactorPlugins.heart = function() {
    return {
        init: function() {
            var button = this.button.add('heart', 'Advanced');
     
            // make your added button as Font Awesome's icon
            this.button.setAwesome('heart', 'fa-heart');
     
            this.button.addCallback(button, this.heart.testButton);
        },
        testButton: function(buttonName) {
            alert(buttonName);
        }
    };
};

RedactorPlugins.cloud = function() {
    return {
        init: function() {
            var button = this.button.add('cloud', 'Advanced');
     
            // make your added button as Font Awesome's icon
            this.button.setAwesome('cloud', 'fa-cloud');
     
            this.button.addCallback(button, this.cloud.testButton);
        },
        testButton: function(buttonName) {
            alert(buttonName);
        }
    };
};

// RedactorPlugins.advanced = function() {
//     return {
//         init: function() {
//             var button = this.button.add('advanced', 'Advanced');
     
//             // make your added button as Font Awesome's icon
//             this.button.setAwesome('advanced', 'fa-tasks');
     
//             this.button.addCallback(button, this.advanced.testButton);
//         },
//         testButton: function(buttonName) {
//             alert(buttonName);
//         }
//     };
// };