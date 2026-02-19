Website Plan Document

CS AI Advisor
1) Core Product Summary
The AI Faculty is an innovative mobile application that provides personalized
academic assistance to students at University. Powered by Gemini’s technology
and integrated with university-specific data, this chat agent helps students navigate their
academic journey with ease.

2) Feature List
AI Agent
- Intelligent Responses: Leverages Gemini for natural, context-aware conversations
- University-Specific Knowledge: Trained on Morgan State University curriculum
data
- Multi-turn Conversations: Maintains context throughout the chat session
- Real-time Typing Indicators: Visual feedback during AI response generation
- Emotional reading
Course &amp; Department Information
- Course Catalog: Browse Morgan State’s complete Computer Science course offerings
- Department Information: Access faculty details and contact info
Firebase Integration
- Firebase Integration: Real-time curriculum data updates

- Firebase Authentication: Secure sign-in with email/password (including Google sign-
in)
- Cloud Firestore: Real-time database
- Firebase Storage: File storage

Account &amp; UX
- Profile Management: View and edit user information
- Morgan State University Pattern Colors
- Secure Logout: Easy session management
- Dark/Light Modes: Automatic theme switching
- Responsive Design
Frontend (Android)
- Android Studio + Kotlin
- Android Speech Recognizer: Voice input
Libraries &amp; Architecture (Android)
- MVVM Pattern: Clean architecture
- StateFlow: Reactive state management
- Dependency Injection: Manual DI
- Gson: JSON serialization

3) Screens / Pages (Planned App/Website Views)
A) Authentication Screens
1. Sign In
o Email/password sign-in
o Google sign-in
2. Sign Up
3. Secure Logout
B) Main Navigation Screens
1. Chat (AI Agent)
o Multi-turn conversation
o Real-time typing indicator
o Emotional reading
o Voice input (Speech Recognizer)
2. Course Catalog
o Browse CS course offerings
3. Department Info
o Faculty details + contact info
4. Profile
o View/edit user information
5. Settings
o Dark/Light mode
o Account options

4) Data Plan (Firebase)
Cloud Firestore Collections (Real-time)
- users
o profile info (name, major, year, etc.)
- courses
o course offerings for CS
- faculty
o department info, contact details
- chat_sessions
o session metadata (userId, timestamps)
- messages
o messages tied to a session (role, content, timestamp)
- curriculum_updates
o used to push real-time curriculum changes

Firebase Storage
- Stores uploaded files (if needed for curriculum files or user documents)

5) App Architecture Plan (Android/Kotlin)
Pattern: MVVM
- View (UI): Activities/Fragments/Compose UI
- ViewModel: State + event handling
- Repository: Firebase operations (Auth, Firestore, Storage)
- Models: Gson-serializable data classes

6) AI Chat Flow (Gemini + Context)
1. User types or speaks → converted to text
2. App writes user message to Firestore (messages)
3. Show typing indicator
4. Gemini generates response using:
o Conversation context (multi-turn)
o Morgan State curriculum data (from Firestore)
o Emotional reading signal (if available)
5. App stores AI response to Firestore
6. UI updates in real-time (Firestore listener)

7) UI/UX Requirements
- Responsive Design: Works on different phone sizes
- Dark/Light Mode: Automatic theme switching
- Typing Indicator: Visible during AI generation
- Profile Management: Edit + save instantly
- Smooth navigation between: Chat / Catalog / Department / Profile
