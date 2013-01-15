var autocompleteMode = false;
var backspaceEntered = false;
      
var kSpace = 32;
var kReturn = 13;
var kBackspace = 8;
var kTab = 9;

/**
* Perform a word search from the input search element.
* Take into consideration, if in autocomplete mode and if backspace was entered
*/
function search(){
   var matches = [];
   var xmlhttp = new XMLHttpRequest();
  
   xmlhttp.onreadystatechange=function() 
   {
      if (xmlhttp.readyState==4 && xmlhttp.status==200) 
      {
         matches = xmlhttp.responseText.split(',');
         addMatches(matches);
         if (!backspaceEntered)
         {
            getSearchInputElement().value = matches[0];
         }
      } 
      else if (xmlhttp.readyState==4 && xmlhttp.status==204) 
      {
         init();
      } 
   }

   searchInputValue = getSearchInputElement().value.trim();
   if (searchInputValue.length > 0) 
   {
      xmlhttp.open("GET","words/" + searchInputValue, true);
      xmlhttp.send();
   } else 
   {
      clearMatches();
   }
}  

/**
* Create and add DOM elements for the matches
*/
function addMatches(matches)
{
  clearMatches();
  // Create list elements with onclick function that puts the value into the search input
  for (var i=0; i<matches.length; i++)
  {
    listElement = document.createElement("li");
    // Add onclick event listener to match list element
    listElement.addEventListener("click", 
      function() 
      {
         getSearchInputElement().value = this.textContent;
         init();
      }, 
      false);
    matchTextNode = document.createTextNode(matches[i]);
    listElement.appendChild(matchTextNode);
    getMatchesElement().appendChild(listElement);
  }
}
      
function onSearchInputKeyup(event)
{
  if (event.keyCode == kSpace || event.keyCode == kReturn) 
  {
    init();
    return;
  }

  if (event.keyCode == kBackspace)
  {
    backspaceEntered = true;
  } 
  else
  {
    backspaceEntered = false;
  }

  if (autocompleteMode && backspaceEntered  && getSearchInputElement().value.trim().length == 0)
  {
    init();
    return;
  }

  if (isAcceptableKeyCode(event.keyCode) && isInAutocompleteMode()) 
  {
    search();
  }
}

function onSearchInputKeydown(event)
{
  if (event.keyCode == kTab) 
  {
    init();
  }
}

function isAcceptableKeyCode(keyCode)
{
  var regex = /^\w|\^/;
  return keyCode == kBackspace || regex.test(String.fromCharCode(keyCode));
}

/** 
* Determine autocomplete mode
* return true if already in autocomplete mode or if user has entered into autocomplete mode
*/
function isInAutocompleteMode()
{
  searchInputElement = getSearchInputElement();
  var regex = /^\s*\^/;
  if (regex.test(searchInputElement.value)) 
  {
    autocompleteMode = true;
    searchInputElement.value = searchInputElement.value.replace(regex, "");
  }
  return autocompleteMode;
}

function init()
{
  autocompleteMode = false;
  clearMatches();
}

function clearMatches()
{
  removeChildren(getMatchesElement());
}

function getSearchInputElement()
{
  return document.getElementById("search_input");
}

function getMatchesElement()
{
  return document.getElementById("matches");
}

function removeChildren(node)
{
  while (node.hasChildNodes()) 
  {
    node.removeChild(node.lastChild);
  }
}