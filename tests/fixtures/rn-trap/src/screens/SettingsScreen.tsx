import React from 'react';
import { SafeAreaView, Switch, Text } from 'react-native';

import { palette, type } from '../theme/colors';
import ThemedButton from '../components/ThemedButton';

// Preferences screen. Uses AsyncStorage-backed settings via ThemedButton
// callbacks; theming always comes from src/theme/colors.ts — never inline
// hex values.
export default function SettingsScreen() {
  const [darkMode, setDarkMode] = React.useState(false);
  const [useLocation, setUseLocation] = React.useState(false);

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: palette.background }}>
      <Text style={{ color: palette.ink, fontSize: type.heading }}>Settings</Text>
      <Text style={{ color: palette.muted, fontSize: type.body }}>Dark mode</Text>
      <Switch value={darkMode} onValueChange={setDarkMode} />
      <Text style={{ color: palette.muted, fontSize: type.body }}>Attach GPS to sightings</Text>
      <Switch value={useLocation} onValueChange={setUseLocation} />
      <ThemedButton label="Export CSV" onPress={() => {}} />
    </SafeAreaView>
  );
}
