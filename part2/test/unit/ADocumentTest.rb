require "test/unit"

require "./ADocument"
require "./ASection"

class ADocumentTest < Test::Unit::TestCase

  	def setup
    	@document = ADocument.new
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

 	def testAddSection
 	 	assert_not_nil addSection
 	 	assert_nil addSection
 	end

 	def testFindSection
 		addSection("header")
 		addSection("body")

 		headerSection = @document.findSection("header")
 		bodySection = @document.findSection("body")

		assert_not_nil headerSection
 		assert_not_nil bodySection
 	end

 	def testAddKey
 	 	@section = addSection
 		
 	 	assert addKey
		assert !addKey
 	end	

 	def test_get_value
		addSectionAndKey

 		assert_equal(@document.getValue(@section.name, "budget"), "45")
 	end	

 	def test_get_string_value
		addSectionAndKey

 		assert_equal(@document.getStringValue(@section.name, "budget"), "45")
 	end	

 	def test_get_integer_value
		addSectionAndKey

 		assert_equal(@document.getIntegerValue(@section.name, "budget"), 45)
 	end

 	def test_get_float_value
		addSectionAndKey

 		assert_equal(@document.getFloatValue(@section.name, "budget"), 45.0)
 	end	

 	def test_set_value_with_string
 		addSectionAndKey
 		@document.setValue("header", "budget", "A really big one")
 		assert_equal(@document.getValue("header", "budget"), "A really big one\r\n")
 	end

 	def test_set_value_with_empty_string
 		addSectionAndKey
 		@document.setValue("header", "budget", "")
 		assert_equal(@document.getValue("header", "budget"), "\r\n")
 	end

 	def test_set_value_with_nil 
 		addSectionAndKey
 		@document.setValue("header", "budget", nil)
 		assert_equal(@document.getValue("header", "budget"), "\r\n")
 	end

 	def test_set_value_with_int 
 		addSectionAndKey
 		@document.setValue("header", "budget", 66)
 		assert_equal(@document.getValue("header", "budget"), "66\r\n")
 	end

 	def test_set_value_with_float 
 		addSectionAndKey
 		@document.setValue("header", "budget", 66.0)
 		assert_equal(@document.getValue("header", "budget"), "66.0\r\n")
 	end

end
