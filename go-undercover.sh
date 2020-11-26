#!/bin/sh

DIR=~/.local/share/go-undercover/
SHARE_DIR=/usr/share/go-undercover/
CONF_FILES=$SHARE_DIR/config/
XFCE4_PANEL_PROFILES=$SHARE_DIR/scripts/xfce4-desktop-profiles.py
GO_UNDERCOVER_PANEL_PROFILE=$SHARE_DIR/go-undercover-panel-profile.tar.bz
USER_PANEL_PROFILE=$DIR/user-panel-profile.tar.bz

mkdir -p $DIR

# Hide existing notifications
killall xfce4-notifyd

set_xconf_settings() {
	xfconf-query -c xsettings -p /Net/ThemeName -n -t string -s "$GTK_THEME"
	xfconf-query -c xfwm4 -p /general/theme -n -t string -s "$WM_THEME"
	xfconf-query -c xfwm4 -p /general/button_layout -n -t string -s "$WM_BUTTON_LAYOUT"
	xfconf-query -c xsettings -p /Net/IconThemeName -n -t string -s "$ICON_THEME"
	xfconf-query -c xsettings -p /Gtk/CursorThemeName -n -t string -s "$CURSOR_THEME"
	xfconf-query -c xsettings -p /Gtk/FontName -n -t string -s "$FONT"
}

enable_undercover() {
	cat <<-EOF > $DIR/lock
		GTK_THEME="$(xfconf-query -c xsettings -p /Net/ThemeName 2> /dev/null)"
		WM_THEME="$(xfconf-query -c xfwm4 -p /general/theme 2> /dev/null)"
		WM_BUTTON_LAYOUT="$(xfconf-query -c xfwm4 -p /general/button_layout 2> /dev/null)"
		ICON_THEME="$(xfconf-query -c xsettings -p /Net/IconThemeName 2> /dev/null)"
		CURSOR_THEME="$(xfconf-query -c xsettings -p /Gtk/CursorThemeName 2> /dev/null)"
		FONT="$(xfconf-query -c xsettings -p /Gtk/FontName 2> /dev/null)"
	EOF
	GTK_THEME='Windows-10'
	WM_THEME='Windows-10'
	WM_BUTTON_LAYOUT='|HMC'
	ICON_THEME='Windows-10-Icons'
	CURSOR_THEME='Windows-10-Icons'
	FONT='Liberation Sans 11'
	set_xconf_settings
	$XFCE4_PANEL_PROFILES save $USER_PANEL_PROFILE
	$XFCE4_PANEL_PROFILES load $GO_UNDERCOVER_PANEL_PROFILE
	(cd $CONF_FILES && \
		find . -type f -exec sh -c \
			'[ -f ~/.config/"$1" ] && mv ~/.config/"$1" ~/.config/"${1}.undercover"' _ {} \;)
	cp -r $CONF_FILES/* ~/.config/
	[ -f ~/.face ] && mv ~/.face ~/.face.undercover
	printf ': undercover && export PS1='\''C:${PWD//\//\\\\\}> '\''\n' >> ~/.bashrc
	printf ': undercover && export PS1='\''C:${PWD//\//\\\\}> '\''\n' >> ~/.zshrc
	printf ': undercover && new_line_before_prompt=no\n' >> ~/.zshrc
}

disable_undercover() {
	. $DIR/lock
	set_xconf_settings
	$XFCE4_PANEL_PROFILES load $USER_PANEL_PROFILE
	(cd $CONF_FILES && \
		find . -type f -exec rm ~/.config/{} \;)
	find ~/.config -name '*.undercover' -exec sh -c \
		'mv "$1" "$(echo $1 | sed 's/.undercover//')"' _ {} \;
	[ -f ~/.face.undercover ] && mv ~/.face.undercover ~/.face
	rm $DIR/lock
	sed -i -e '/: undercover/d' ~/.bashrc ~/.zshrc
}

if [ -f $DIR/lock ]; then
	disable_undercover
	sleep 1
	notify-send -i dialog-information 'Desktop settings restored'
else
	enable_undercover
fi
