// SPDX-License-Identifier: MIT
pragma solidity >0.4.0;
// import library file
pragma experimental ABIEncoderV2;
// activate experimental features

contract userRecords {
  // enum type variable to store user gender
  enum genderType { male, female }
  // Actual user object which we will store
  struct user{
    string name;
    genderType gender;
  }
  // user object
  user user_obj;

  // this data structure maps a string to array of strings
  mapping(string => string[]) userId2FileNames;

  // Internal function to convert genderType enum from string
  function getGenderFromString(string memory gender) pure internal returns (genderType) {
    if(keccak256(bytes (gender)) == keccak256("male")) {
      return genderType.male;
    } else {
      return genderType.female;
    }
  }
  //Internal function to convert genderType enum to string
  function getGenderToString(genderType gender) pure internal returns (string memory) {
    if(gender == genderType.male) {
      return "male";
    } else {
      return "female";
    }
  }
  // set user public function
  // This is similar to persisting object in db.
  function setUser(string memory name, string memory gender) payable public {
    genderType gender_type = getGenderFromString(gender);
    user_obj = user({name:name, gender: gender_type});
  }

  // get user public function
  // This is similar to getting object from db.
  function getUser() public view returns (string memory, string memory) {
    return (user_obj.name, getGenderToString(user_obj.gender));
  }

  // pushes a string into array mapping
  function addFiles(string memory id, string memory file) public {
      userId2FileNames[id].push(file);
  }

  // gets list of strings from array mapping
  function getFiles(string memory id) public returns (string[] memory) {
           return userId2FileNames[id];
  }

  // removes a particular string from array mapping
  function remFiles(string memory id, string memory file) public {
    uint index = userId2FileNames[id].length;
    for(uint i=0; i<index; i++)
    {
      if(keccak256(bytes (userId2FileNames[id][i])) == keccak256(bytes (file)))
      {
        delete userId2FileNames[id][i];
        break;
      }
    }
  }

}