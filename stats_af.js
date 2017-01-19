#!/usr/bin/env mongo

var compare = function (x, y) { return y.count - x.count };

db = new Mongo().getDB("ccanalysis");

var collection = db.getCollection(project);
if (undefined == collection)
   return;

var result = { 
   project : project, 
   others : collection.aggregate(
      { $match : { _class : "clone.analysis.Stats"} },
      { $project : {
                     _id : 0,
                     totalStaticCalls : 1,
                     totalMethods : 1,
                     totalClasses : 1,
                     totalPackages : 1,
                     totalClassesNotDirectlyInheritingTestCase : 1,
                     totalClassesContainingNonEmptySetupOrTeardown : 1,
                     totalMethodsWithAtLeast5Asserts : 1,
                     totalMethodsWithBranches : 1,
                     totalMethodsWithLoops : 1,
                     totalMethodsWithNoStaticCalls : 1,
                     totalMethodsWithNetworkAccess : 1,
                     totalMethodsWithFilesystemAccess : 1
                   }
      }
   ).toArray()[0],
   detail : {} 
};

var raw_filter = {
   _class : "clone.analysis.similarity.StaticCallFlowMatchSet", 
};

var filter = { 
   _class : raw_filter._class,
   isHighPriority : true 
};

result.detail.sets = 
{
   hist   : 
            collection.aggregate(
               { $match : raw_filter },
               { $group : {_id : "$isHighPriority", count : {$sum : 1} } },
               { $sort : {_id : -1} }
            ).toArray()
};

result.detail.packages = 
{
   hist   : 
            collection.aggregate(
               { $match : filter },
               { $group : {_id : "$packageCount", count : {$sum : 1} } },
               { $sort : {_id : 1} }
            ).toArray(),
};

result.detail.classes = 
{
   hist   : 
            collection.aggregate(
               { $match : filter },
               { $group : {_id : "$classCount", count : {$sum : 1} } },
               { $sort : {_id : 1} }
            ).toArray(),
};

result.detail.methods = 
{
   hist   : 
            collection.aggregate(
               { $match : filter },
               { $group : {_id : "$_id", count_ : {$first : {$size : "$set"}}} },
               { $group : {_id : "$count_", count : {$sum : 1} } },
               { $sort : {_id : -1} }
            ).toArray(),
};

result.detail.asserts = 
{
   hist   : 
            collection.aggregate(
               { $match : filter },
               { $unwind : "$set" }, 
               { $group : {_id : "$_id", count_ : {$first : {$size : "$set.staticCalls"}}} },
               { $group : {_id : "$count_", count : {$sum : 1} } },
               { $sort : {_id : -1} }
            ).toArray(),
};

result.detail.assertsPerMethod = 
{
   hist   : 
            collection.aggregate(
               { $match : filter },
               { $unwind : "$set" }, 
               { $group : {_id : "$set.staticCalls", count_ : {$first : {$size : "$set.staticCalls"}}} },
               { $group : {_id : "$count_", count : {$sum : 1} } },
               { $sort : {_id : -1} }
            ).toArray(),
};

result.detail.controlFlowSizes = 
{
   hist   : 
            collection.aggregate(
               { $match : filter },
               { $unwind : "$set" }, 
               { $group : {_id : "$_id", count_ : {$first : "$set.controlFlowSize"}} },
               { $group : {_id : "$count_", count : {$sum : 1} } },
               { $sort : {_id : -1} }
            ).toArray(),
};

result.detail.controlFlowSizesPerMethod = 
{
   hist   : 
            collection.aggregate(
               { $match : filter },
               { $unwind : "$set" }, 
               { $group : {_id : "$set.staticCalls", count_ : {$first : "$set.controlFlowSize"}} },
               { $group : {_id : "$count_", count : {$sum : 1} } },
               { $sort : {_id : -1} }
            ).toArray(),
};

result.detail.uniquenesses = 
{
   hist   : 
            collection.aggregate(
               { $match : filter },
               { $unwind : "$set" }, 
               { $group : {_id : "$_id", count_ : {$first : "$set.uniqueness"}} },
               { $group : {_id : "$count_", count : {$sum : 1} } },
               { $sort : {_id : -1} }
            ).toArray(),
};

result.detail.uniquenessesPerMethod = 
{
   hist   : 
            collection.aggregate(
               { $match : filter },
               { $unwind : "$set" }, 
               { $group : {_id : "$set.staticCalls", count_ : {$first : "$set.uniqueness"}} },
               { $group : {_id : "$count_", count : {$sum : 1} } },
               { $sort : {_id : -1} }
            ).toArray(),
};

result.detail.relevantCloneSets = 
{
   hist   : 
            collection.aggregate(
               { $match : filter },
               { $group : {_id : {$ne : [0, {$size : "$relevantCloneSets"}]}, count : {$sum : 1} } },
               { $sort : {_id : -1} }
            ).toArray()
};

printjson(result);
