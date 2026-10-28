import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';
import { palette, type } from '../theme/colors';

// THE app-wide button. If you need a button, use this one — don't create a
// second button component. Tone variants map to the token palette.
type Props = {
  label: string;
  onPress: () => void;
  tone?: 'primary' | 'quiet';
};

export default function ThemedButton({ label, onPress, tone = 'primary' }: Props) {
  const bg = tone === 'primary' ? palette.accent : palette.surface;
  const fg = tone === 'primary' ? '#ffffff' : palette.ink;
  return (
    <TouchableOpacity onPress={onPress} style={[styles.base, { backgroundColor: bg }]}>
      <Text style={[styles.label, { color: fg, fontSize: type.body }]}>{label}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  base: { paddingVertical: 12, paddingHorizontal: 20, borderRadius: 10 },
  label: { fontWeight: '600' },
});
