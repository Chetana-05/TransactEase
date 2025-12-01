import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Button, Text, Surface, useTheme } from 'react-native-paper';
import Voice, { SpeechResultsEvent } from '@react-native-community/voice';
import Tts from 'react-native-tts';

const VoiceAssistantScreen = () => {
  const theme = useTheme();
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [conversation, setConversation] = useState<Array<{ type: 'user' | 'ai', text: string }>>([]);

  useEffect(() => {
    // Initialize voice recognition
    Voice.onSpeechResults = onSpeechResults;
    Voice.onSpeechError = onSpeechError;
    Voice.onSpeechEnd = onSpeechEnd;

    // Initialize TTS
    Tts.setDefaultLanguage('en-US');
    Tts.setDefaultRate(0.5);

    return () => {
      Voice.destroy().then(Voice.removeAllListeners);
    };
  }, []);

  const onSpeechResults = (e: SpeechResultsEvent) => {
    if (e.value) {
      const text = e.value[0];
      setTranscript(text);
      setConversation(prev => [...prev, { type: 'user', text }]);
      processUserCommand(text);
    }
  };

  const onSpeechError = (e: any) => {
    console.error(e);
    setIsListening(false);
  };

  const onSpeechEnd = () => {
    setIsListening(false);
  };

  const processUserCommand = async (command: string) => {
    // Simple command processing logic - replace with actual AI processing
    let response = '';
    const lowerCommand = command.toLowerCase();

    if (lowerCommand.includes('transaction status')) {
      response = 'Your latest transaction of $100 to John Doe is pending. Expected completion time is 2 minutes.';
    } else if (lowerCommand.includes('balance')) {
      response = 'Your current balance is $1,500.';
    } else if (lowerCommand.includes('recent transactions')) {
      response = 'You have 2 recent transactions. One completed payment of $200 to Jane Smith, and one pending payment of $100 to John Doe.';
    } else {
      response = 'I\'m sorry, I didn\'t understand that command. You can ask about transaction status, balance, or recent transactions.';
    }

    setAiResponse(response);
    setConversation(prev => [...prev, { type: 'ai', text: response }]);
    await Tts.speak(response);
  };

  const startListening = async () => {
    try {
      await Voice.start('en-US');
      setIsListening(true);
    } catch (e) {
      console.error(e);
    }
  };

  const stopListening = async () => {
    try {
      await Voice.stop();
      setIsListening(false);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.conversationContainer}>
        {conversation.map((message, index) => (
          <Surface key={index} style={[
            styles.messageBubble,
            message.type === 'user' ? styles.userMessage : styles.aiMessage
          ]}>
            <Text style={styles.messageText}>{message.text}</Text>
          </Surface>
        ))}
      </ScrollView>
      
      <View style={styles.controls}>
        <Button
          mode="contained"
          onPress={isListening ? stopListening : startListening}
          style={[styles.button, { backgroundColor: isListening ? theme.colors.error : theme.colors.primary }]}
        >
          {isListening ? 'Stop Listening' : 'Start Listening'}
        </Button>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  conversationContainer: {
    flex: 1,
    padding: 16,
  },
  messageBubble: {
    padding: 12,
    marginVertical: 4,
    borderRadius: 16,
    maxWidth: '80%',
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#2196F3',
  },
  aiMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#FFFFFF',
  },
  messageText: {
    color: '#000000',
  },
  controls: {
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  button: {
    marginVertical: 8,
  },
});

export default VoiceAssistantScreen; 