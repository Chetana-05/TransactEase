import React, { useState, useEffect } from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import { FAB, Card, Title, Paragraph, useTheme } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import Tts from 'react-native-tts';

interface Transaction {
  id: string;
  amount: number;
  status: 'pending' | 'completed' | 'failed';
  timestamp: string;
  recipient: string;
}

const HomeScreen = () => {
  const navigation = useNavigation();
  const theme = useTheme();
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  useEffect(() => {
    // Initialize TTS
    Tts.setDefaultLanguage('en-US');
    Tts.setDefaultRate(0.5);

    // Mock data - replace with actual API calls
    setTransactions([
      {
        id: '1',
        amount: 100,
        status: 'pending',
        timestamp: new Date().toISOString(),
        recipient: 'John Doe',
      },
      {
        id: '2',
        amount: 200,
        status: 'completed',
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        recipient: 'Jane Smith',
      },
    ]);
  }, []);

  const getStatusColor = (status: Transaction['status']) => {
    switch (status) {
      case 'completed':
        return '#4CAF50';
      case 'pending':
        return '#FFC107';
      case 'failed':
        return '#F44336';
      default:
        return '#757575';
    }
  };

  const renderTransaction = ({ item }: { item: Transaction }) => (
    <Card style={styles.card} onPress={() => navigation.navigate('Transaction', { transaction: item })}>
      <Card.Content>
        <Title>${item.amount}</Title>
        <Paragraph>To: {item.recipient}</Paragraph>
        <Paragraph>Time: {new Date(item.timestamp).toLocaleString()}</Paragraph>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
          <Paragraph style={styles.statusText}>{item.status.toUpperCase()}</Paragraph>
        </View>
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={transactions}
        renderItem={renderTransaction}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
      />
      <FAB
        style={[styles.fab, { backgroundColor: theme.colors.primary }]}
        icon="microphone"
        onPress={() => navigation.navigate('VoiceAssistant')}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  list: {
    padding: 16,
  },
  card: {
    marginBottom: 16,
    elevation: 4,
  },
  statusBadge: {
    position: 'absolute',
    top: 16,
    right: 16,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
  },
});

export default HomeScreen; 