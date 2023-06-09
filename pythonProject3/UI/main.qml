import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 4000
    height: 6000
    title: "HelloApp"

Rectangle {
        anchors.fill: parent

Image {
            sourceSize.width: parent.width
            sourceSize.height: parent.height
            source: ".17545.jpg"
            fillMode: Image.PreserveAspectCrop
        }

Rectangle {
            anchors.fill: parent
            color: "transparent"
            Text {
                anchors {
                    bottom: parent.bottom
                    bottomMargin: 12
                    left: parent.left
                    leftMargin: 12
                }
                text: "16:38:33"
                font.pixelSize: 24
            }
        }
    }
}