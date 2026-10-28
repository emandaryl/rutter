import React, { useEffect, useState } from 'react';
import { SafeAreaView, FlatList, Text } from 'react-native';

import { fetchSightings } from '../lib/apiClient';
import { palette, type } from '../theme/colors';
import ThemedButton from '../components/ThemedButton';

// Lists the user's recent bird sightings. Data comes exclusively through
// apiClient — screens never fetch directly.
export default function HomeScreen() {
  const [sightings, setSightings] = useState([]);
  const [error, setError] = useState<null | string>(null);

  useEffect(() => {
    fetchSightings()
      .then(setSightings)
      .catch(() => setError('Could not load sightings. Pull to try again.'));
  }, []);

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: palette.background }}>
      {error !== null && <Text style={{ color: palette.danger }}>{error}</Text>}
      <FlatList
        data={sightings}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <Text style={{ color: palette.ink, fontSize: type.body }}>
            {item.species} — {item.where}
          </Text>
        )}
      />
      <ThemedButton label="Log a sighting" onPress={() => {}} />
    </SafeAreaView>
  );
}
