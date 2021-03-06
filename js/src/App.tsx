import * as React from 'react';
import { MyRichTextEditor } from './components';
import 'semantic-ui-css/semantic.min.css';
import './App.css';

const logo = require('./logo.svg');

class App extends React.Component {
  render() {
    return (
      <div className="App">
        <div className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h2>Welcome to React</h2>
        </div>
        <p className="App-intro">
          <MyRichTextEditor />
        </p>
      </div>
    );
  }
}

export default App;
