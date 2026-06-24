# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem


def _item(model, label):
    return PluginMenuItem(
        link=f"plugins:netbox_system_services:{model}_list",
        link_text=label,
        buttons=[
            PluginMenuButton(
                f"plugins:netbox_system_services:{model}_add", "Add", "mdi mdi-plus-thick"
            )
        ],
    )


menu = PluginMenu(
    label="System Services",
    groups=(
        ("System", (_item("systemconfig", "System Config"),)),
        (
            "SNMP",
            (
                _item("snmpconfig", "SNMP Config"),
                _item("snmpcommunity", "SNMP Communities"),
                _item("snmptraptarget", "SNMP Trap Targets"),
            ),
        ),
        (
            "Syslog",
            (_item("syslogconfig", "Syslog Config"), _item("syslogserver", "Syslog Servers")),
        ),
        ("NTP", (_item("ntpconfig", "NTP Config"), _item("ntpserver", "NTP Servers"))),
        (
            "DNS",
            (
                _item("dnsresolverconfig", "DNS Resolver Config"),
                _item("dnsforwardzone", "DNS Forward Zones"),
                _item("dynamicdnsrecord", "Dynamic DNS Records"),
            ),
        ),
        ("System Tunables", (_item("systemtunable", "System Tunables"),)),
    ),
    icon_class="mdi mdi-cog-transfer",
)
