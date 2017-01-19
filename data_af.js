#!/usr/bin/env mongo

var compare = function (x, y) { return y.count - x.count };

db = new Mongo().getDB("ccanalysis");

var collection = db.getCollection(project);
if (undefined == collection)
   return;

var result = { 
   project : project, 
};

var filter = { 
   _class : "clone.analysis.similarity.StaticCallFlowMatchSet", 
   isHighPriority : true 
};

result.data = collection.aggregate(
   { $match : filter },
   { $unwind : "$set" },
   { $group : { 
                  _id : { 
                     _id : "$_id", 
                     packageCount : "$packageCount", 
                     classCount : "$classCount" 
                  },
                  asserts : { $first : { $size : "$set.staticCalls" } },
                  methods : { $sum : 1 }
              }
   },
   { $project : { 
                  _id : "$_id._id",
                  packages : "$_id.packageCount", 
                  classes : "$_id.classCount", 
                  asserts : 1,
                  methods : 1
               },
   },
   { $sort : { 
                  asserts : -1, 
                  methods : 1, 
                  packages : 1, 
                  classes : 1 
             } 
   }
).toArray();

for (var i = 0; i < result.data.length; ++i)
   result.data[i]._id = result.data[i]._id.valueOf();

printjson(result);
