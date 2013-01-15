require "test/unit"

require "./AParser"
require "./ADocument"

class AParserTest < Test::Unit::TestCase

   def setup
      @document = ADocument.new
    	@parser = AParser.new
    	@section = nil
  	end	

  	def addSection(sectionName="header")
  		@section = @document.addSection(sectionName)
  	end

  	def addKey
  		@section.addKey("budget","45")
  	end

  	def addSectionAndKey
  		@section = addSection
  		addKey
  	end

 	def testGetSectionName 
 		sectionName = @parser.send(:getSectionName, "[ meta data ]  \r\n ")

 		assert_equal("meta data", sectionName)
 	end

 	def testGetKeyValuePair 
 		keyValuePair = @parser.send(:getKeyValuePair, " budget : 45 \r\n ")

 		assert_equal(" budget : 45 \r", keyValuePair)
 	end

 	def testGetContinuedValue 
 		continuedValue = @parser.send(:getContinuedValue, " more text \r\n ")

 		assert_equal(" more text \r", continuedValue)
 	end

 	def testGetContinuedValue_when_starting_at_0
 		continuedValue = @parser.send(:getContinuedValue, "more\r\n")

 		assert_nil(continuedValue)
 	end

 	def testParseSection
 		section = @parser.send(:parseSection, "[ meta data ]  \r\n ", 1, @document)

 		assert_not_nil(section)
 		assert_equal("meta data", section.name)
 	end

  	def testParseSection_when_duplicate
  		addSection
  
  		assert_raise(RuntimeError) { 
         @parser.send(:parseSection, "[header]\r\n", 1, @document)
  		} 		
 	end	

 	def testParseSection_when_not_starting_at_0
 		section = @parser.send(:parseSection, " [ meta data ]  \r\n", 1, @document)

 		assert_nil(section)
 	end
 	
 	def testParseKey
 		addSection
 		lineNbr = 2
 		key = @parser.send(:parseKey, "budget : 45 \r\n", lineNbr, @section)
 		
      value = @document.getValue("header", "budget")

 		assert_equal("budget", key)
 		assert_equal(" 45 \r\n", value)
 	end

 	def testParseKey_when_duplicate
 		addSectionAndKey
 		currentSection = ASection.new("header")
 		lineNbr = 3
 		
 		assert_raise(RuntimeError) { 
         @parser.send(:parseKey, "budget:75", lineNbr, @section)
			# ADocument.parseKey("budget:75", lineNbr, @section)
  		}
 	end 	
 	
 	def testParseContinuedValue
 		currentSection = ASection.new("header")
 		currentSection.addKey("description", "some description text")
 		currentKey = "description"

 		continuedValue = @parser.send(:parseContinuedValue, " more description text\r\n", currentSection, currentKey)

 		assert_equal(" more description text\r\n", continuedValue)
 	end	

end
