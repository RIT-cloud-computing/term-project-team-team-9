import logo from './logo.svg';
import './App.css';
const AWS = require("aws-sdk");

function App() {

  AWS.config.update({
    region: "us-east-2",
    accessKeyId: "AKIAVALXZ3LQAMGHEP6Z",
    secretAccessKey: "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"
  });
  let docClient = new AWS.DynamoDB.DocumentClient();
  
  let params = {
    TableName: "jaywalker",
    ScanIndexForward: true
  };
  
  let items = docClient.scan(params, function(err, data) {
    if (err) {
      console.error("Unable to query. Error:", JSON.stringify(err, null, 2));
    } else {
      console.log("Data retrieved", data);
      for(let i of data.Items) {
        i.Date = new Date(i.Date);
      }
      data.Items.sort((a,b) => {
        return b.Date - a.Date;
      })
      console.log('Image', data.Items[0].Image);
      return (<img src={data.Items[0].Image}>"Test"</img>)
    }
  });

  console.log(items);

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <p>
          {items}
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
