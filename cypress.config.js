const fs = require('fs-extra')
const path = require('path')

//read port and flowsheet name from shared_variable.json
const sharedVariables = JSON.parse(
  fs.readFileSync(
    path.join(__dirname, "/shared_variable.json")
  )
);

module.exports = {
  e2e: {
    baseUrl: sharedVariables.url,
    video : false
  }
}
