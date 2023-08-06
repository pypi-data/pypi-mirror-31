    function open_menu(x, y) {
        popup_menu.x = x
        popup_menu.y = y
        popup_menu.visible = true
    }


    Rectangle {
        id: popup_menu
        visible: false
        width: 100
        height: 300
        border.width: 1

        ListView {
            anchors.fill: parent
            anchors.margins: Style.spacing.base
            spacing: Style.spacing.base_vertical

            model: directory_model

            delegate: Row {
                Button {
                    text: name
                    onClicked: {
                        popup_menu.visible = false
                        console.info('Clicked on item', model.index)
                    }
                }
            }
        }
    }


                    // menu.popup()
                    // open_menu(item.x + item.width, item.y + item.height)
                }

                Instantiator {
                    model: directory_model
                    MenuItem {
                        text: model.name
                    }
                }


                Repeater {
                    model: directory_model
                
                    MenuItem {
                        text: name
                        // onTriggered:
                    }
                }


                //Component.onCompleted: {
                //    console.info('Menu', model.name)
                //    // for (var i = 0; i < directory_model.length; i++) {
                //    for (var i = 0; i < 10; i++) {
                //        var directory = {'text': 'dir' + i} // directory_model[i]
                //        console.info('add subenu', i, directory)
                //        menu.addItem('foo')
                //    }
                // }
