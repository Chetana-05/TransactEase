# TransactEase
A mobile application that provides real-time transaction monitoring with AI voice assistance to help users track their transactions and get instant updates.

# AI-Powered Transaction Tracker

## Features

- Real-time transaction monitoring
- AI voice assistant for transaction queries
- Voice-to-text and text-to-voice capabilities
- Transaction status tracking with progress indicators
- Instant notifications and updates
- Modern and intuitive UI

## Prerequisites

- Node.js (v14 or later)
- npm or yarn
- React Native development environment
- Android Studio (for Android development)
- Xcode (for iOS development, macOS only)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd transaction-tracker
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Install iOS dependencies (macOS only):
```bash
cd ios
pod install
cd ..
```

4. Start the Metro bundler:
```bash
npm start
# or
yarn start
```

5. Run the application:
```bash
# For Android
npm run android
# or
yarn android

# For iOS (macOS only)
npm run ios
# or
yarn ios
```

## Voice Commands

The AI voice assistant supports the following commands:
- "Check transaction status"
- "What's my balance"
- "Show recent transactions"

## Project Structure

```
src/
  ├── screens/
  │   ├── HomeScreen.tsx       # Main screen with transaction list
  │   ├── TransactionScreen.tsx # Detailed transaction view
  │   └── VoiceAssistantScreen.tsx # AI voice assistant interface
  └── components/             # Reusable components
```

## Technologies Used

- React Native
- TypeScript
- React Navigation
- React Native Paper
- React Native Voice
- React Native TTS
- Socket.IO Client

