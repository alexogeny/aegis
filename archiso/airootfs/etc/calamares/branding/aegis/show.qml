/* Aegis Linux - Calamares Slideshow
 * Catppuccin Mocha Theme
 */

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: presentation
    anchors.fill: parent
    color: "#1e1e2e"

    property int currentSlide: 0
    property var slides: [
        {
            title: "Welcome to Aegis Linux",
            description: "A security-focused Arch Linux distribution designed for privacy enthusiasts.",
            icon: "🛡️"
        },
        {
            title: "Security by Default",
            description: "Comprehensive AppArmor profiles, kernel hardening, and nftables firewall protect your system out of the box.",
            icon: "🔒"
        },
        {
            title: "Full Disk Encryption",
            description: "LUKS2 encryption keeps your data safe. Your privacy is our priority.",
            icon: "🔐"
        },
        {
            title: "Beautiful Desktop",
            description: "Hyprland with Catppuccin Mocha theming provides a modern, elegant experience.",
            icon: "✨"
        },
        {
            title: "NVIDIA Ready",
            description: "Full NVIDIA support with open kernel modules for the best Wayland experience.",
            icon: "🎮"
        },
        {
            title: "Getting Started",
            description: "After installation, check 'aa-status' for AppArmor profiles and 'nft list ruleset' for firewall rules.",
            icon: "🚀"
        }
    ]

    Timer {
        interval: 5000
        running: true
        repeat: true
        onTriggered: {
            currentSlide = (currentSlide + 1) % slides.length
        }
    }

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 30
        width: parent.width * 0.8

        Text {
            Layout.alignment: Qt.AlignHCenter
            text: slides[currentSlide].icon
            font.pixelSize: 72
        }

        Text {
            Layout.alignment: Qt.AlignHCenter
            text: slides[currentSlide].title
            font.pixelSize: 32
            font.bold: true
            color: "#cba6f7"
        }

        Text {
            Layout.alignment: Qt.AlignHCenter
            Layout.maximumWidth: parent.width
            text: slides[currentSlide].description
            font.pixelSize: 18
            color: "#cdd6f4"
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
        }
    }

    Row {
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 30
        spacing: 10

        Repeater {
            model: slides.length
            Rectangle {
                width: 12
                height: 12
                radius: 6
                color: index === currentSlide ? "#cba6f7" : "#45475a"

                MouseArea {
                    anchors.fill: parent
                    onClicked: currentSlide = index
                }
            }
        }
    }
}
