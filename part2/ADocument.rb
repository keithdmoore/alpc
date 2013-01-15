require 'active_support/core_ext/string'

#
# This class represents a document and containes zero or more ASection objects
#
class ADocument
   attr_accessor :sections

   def initialize
      super()
      self.sections = []
   end

   def addSection(sectionName)
      if findSection(sectionName)
         return nil
      end
      
      section = ASection.new(sectionName)
      self.sections << section
      
      return section
   end  
   
   def findSection(sectionName)
      return self.sections.detect {|s| s.name == sectionName}
   end
      
   def getValue(sectionName, key)
      section = findSection(sectionName)
      return section ? section.getValue(key) : nil
   end

   def getStringValue(sectionName, key)
      return getValue(sectionName, key)
   end
      
   def getIntegerValue(sectionName, key)
      return getValue(sectionName, key).to_i
   end

   def getFloatValue(sectionName, key)
      return getValue(sectionName, key).to_f
   end

   def setValue(sectionName, key, value)
      section = findSection(sectionName)
      if section
         if value
            newValue = "#{value}\r\n"
         else
            newValue = "\r\n"
         end
         section.setValue(key, newValue)
      end
      return nil
   end      
   
   def to_s
      sectionsString = ""
      self.sections.each do |s|
        sectionsString += "#{s.to_s}\r\n"
      end  
      return sectionsString.chomp
   end 

   def write(filename)
      begin
         file = File.new(filename, "w")
         file.write(self.to_s)
         file.close
      rescue => err
         puts("Exception: #{err}")
         puts(err.backtrace)
         return err
      end
      return nil
   end 

end