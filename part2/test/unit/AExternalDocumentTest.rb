require "test/unit"

require "./ADocument"
require "./AParser"

class AExternalDocumentTest < Test::Unit::TestCase
	KDataDir = "test/data"

	def setup
		@parser = AParser.new
		@document = @parser.createDocumentFrom("#{KDataDir}/input.txt")
	end

	def testCreateDocumentFrom
		headerSection = @document.findSection("header")
		puts headerSection.inspect

		metaDataSection = @document.findSection("meta  data")
		trailerSection = @document.findSection("trailer")

		projectValue = @document.getValue("header", "project")
		headerBudgetValue = @document.getValue("header", "budget")
		accessedValue = @document.getValue("header", "accessed")

		descriptionValue = @document.getValue("meta  data", "description")
		correctionTextValue = @document.getValue("meta  data", "correction text")
		
		trailerBudgetValue = @document.getValue("trailer", "budget")

		assert headerSection
		assert projectValue
		assert headerBudgetValue
		assert accessedValue

		assert metaDataSection
		assert descriptionValue
		assert correctionTextValue

		assert trailerSection
		assert trailerBudgetValue
	end
		
	def testChangeHeaderBudget
		@document.setValue("header", "budget", 77)
		@document.write("#{KDataDir}/change_budget.txt")
	end

	def testChangeTrailerBudgetWithContinuedValue
		@document.setValue("trailer", "budget", "I hope there is still money because I want work\r\n this is a continued value\r\n")
		@document.write("#{KDataDir}/change_budget_with_continued_value.txt")
	end

	def testUseOutputAsinput
		@document.write("#{KDataDir}/generated_input.txt")
		
		@document2 = @parser.createDocumentFrom("#{KDataDir}/generated_input.txt")
		@document2.write("#{KDataDir}/output_from_generated_input.txt")
	end

end