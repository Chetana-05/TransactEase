import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Card, Title, Paragraph, ProgressBar, Button, useTheme } from 'react-native-paper';
import { useRoute, useNavigation } from '@react-navigation/native';
import Tts from 'react-native-tts';

interface Transaction {
  id: string;
  amount: number;
  status: 'pending' | 'completed' | 'failed';
  timestamp: string;
  recipient: string;
}

const TransactionScreen = () => {
  const theme = useTheme();
  const route = useRoute();
  const navigation = useNavigation();
  const [transaction, setTransaction] = useState<Transaction | null>(null);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Initialize TTS
    Tts.setDefaultLanguage('en-US');
    Tts.setDefaultRate(0.5);

    // Get transaction from route params
    const { transaction: routeTransaction } = route.params as { transaction: Transaction };
    setTransaction(routeTransaction);

    // Simulate transaction progress
    if (routeTransaction.status === 'pending') {
      const interval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 1) {
            clearInterval(interval);
            return 1;
          }
          return prev + 0.1;
        });
      }, 1000);
    } else {
      setProgress(1);
    }

    return () => {
      // Cleanup interval if component unmounts
      if (routeTransaction.status === 'pending') {
        clearInterval(interval);
      }
    };
  }, [route.params]);

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

  const speakStatus = async () => {
    if (transaction) {
      const statusMessage = `Transaction of $${transaction.amount} to ${transaction.recipient} is ${transaction.status}.`;
      await Tts.speak(statusMessage);
    }
  };

  if (!transaction) {
    return (
      <View style={styles.container}>
        <Title>Transaction not found</Title>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title>Transaction Details</Title>
          <Paragraph>Amount: ${transaction.amount}</Paragraph>
          <Paragraph>Recipient: {transaction.recipient}</Paragraph>
          <Paragraph>Time: {new Date(transaction.timestamp).toLocaleString()}</Paragraph>
          <Paragraph>Status: {transaction.status.toUpperCase()}</Paragraph>
          
          <View style={styles.progressContainer}>
            <ProgressBar
              progress={progress}
              color={getStatusColor(transaction.status)}
              style={styles.progressBar}
            />
            <Paragraph style={styles.progressText}>
              {Math.round(progress * 100)}% Complete
            </Paragraph>
          </View>

          <Button
            mode="contained"
            onPress={speakStatus}
            style={styles.button}
          >
            Speak Status
          </Button>

          {transaction.status === 'pending' && (
            <Button
              mode="outlined"
              onPress={() => navigation.navigate('VoiceAssistant')}
              style={styles.button}
            >
              Ask AI Assistant
            </Button>
          )}
        </Card.Content>
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  card: {
    margin: 16,
    elevation: 4,
  },
  progressContainer: {
    marginVertical: 16,
  },
  progressBar: {
    height: 8,
    borderRadius: 4,
  },
  progressText: {
    textAlign: 'center',
    marginTop: 8,
  },
  button: {
    marginTop: 8,
  },
});

export default TransactionScreen; 