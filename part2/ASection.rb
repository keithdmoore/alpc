#
# This class represents a section within ADocument
# It contains zero or more key value pairs
#
class ASection
   attr_accessor :name, :keyValuePairs
   
   def initialize(name)
      super()
      self.name = name
      self.keyValuePairs = {}
   end

   def addKey(key, value)
      if keyValuePairs.has_key?(key)
         return false
      else  
         keyValuePairs[key] = value
         return true
      end 
   end

   def appendValue(current_key, value)
      self.keyValuePairs[current_key] += value
      return nil
   end  

   def getValue(key)
      return self.keyValuePairs[key]
   end

   def setValue(key, value)
      self.keyValuePairs[key] = value
      return nil
   end  

   def to_s
      keyValuePairsString = "[#{self.name}]\r\n"
      self.keyValuePairs.each_pair do |k,v|
         keyValuePairsString += "#{k}:#{v}"
      end
      return keyValuePairsString
   end

end