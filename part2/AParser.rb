#
# The class is responsible for creating ADocument from a file
#
class AParser

   def createDocumentFrom(filename)
      counter = 1 
      document = ADocument.new
      @currentSection = nil
      @currentKey = nil
    	begin
         file = File.open(filename, "r")
         
         while (line = file.gets)
    		   puts("#{counter}: #{line}")
            counter = counter + 1
            if line.strip.present?
               if parseSection(line, counter, document)
                  @currentKey = nil
               elsif parseKey(line, counter, @currentSection)
               elsif parseContinuedValue(line, @currentSection, @currentKey)
               end 
            end 
    		end
    		file.close
    	rescue => err
         puts("Exception: #{err}")
         puts(err.backtrace)
    		return err
    	end
      return document
  	end	

  	private 

    def getSectionName(line)
       regex = /^\[.*\]/
       section_name_match = regex.match(line)
       section_name_match ? section_name_match.to_s.gsub("[","").gsub("]","").strip : nil
    end
      
    def parseSection(line, counter, document)
       sectionName = getSectionName(line)
       if sectionName.present?
          @currentSection = document.addSection(sectionName)
          raise "Duplicate Section [#{sectionName}] found on line: #{counter}]" unless @currentSection
          return @currentSection
       end
       return nil
    end

    def getKeyValuePair(line)  
       keyRegex = /^.*:.*/
       keyValuePairMatch = keyRegex.match(line)
       keyValuePairMatch ? keyValuePairMatch.to_s : nil
    end

    def parseKey(line, counter, section)
       keyValuePair = getKeyValuePair(line)
       if keyValuePair.present?
         array = keyValuePair.split(":")
         @currentKey = array[0].strip
         raise "Duplicate key '#{@currentKey}' found on line #{counter}" unless section.addKey(@currentKey, "#{array[1].chomp}\r\n")
         return @currentKey
       end 
       return nil
    end

    def getContinuedValue(line)
       continued_value_regex = /^\s+.+/
       continued_value_match = continued_value_regex.match(line)
       continued_value_match ? continued_value_match.to_s : nil 
    end

    def parseContinuedValue(line, section, key)
       continuedValue = getContinuedValue(line)
       if continuedValue.present?
          continuedValue = "#{continuedValue.chomp}\r\n"
          section.appendValue(key, continuedValue)
          return continuedValue
       end
       return nil    
    end
end