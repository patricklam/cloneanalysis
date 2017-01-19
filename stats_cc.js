#!/usr/bin/env mongo

var thresholds = [0.5, 0.6, 0.7, 0.8, 0.9];

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
   details : [] 
};

for (var j = 0; j < thresholds.length; ++j) {
   var detail = { threshold : thresholds[j] };
   var filter = { _class : "clone.analysis.similarity.CallChainMatchSet", score : { $gte : thresholds[j] } };
   detail.sets = collection.count(filter);
   detail.classes = collection.aggregate(
      { $match : filter },
      { $unwind : "$set" }, 
      { $group : { _id : {className : "$set.className"} } } 
   ).itcount();
   detail.methods = collection.aggregate(
      { $match : filter },
      { $unwind : "$set" }, 
      { $group : { _id : {className : "$set.className", methodName : "$set.methodName"} } } 
   ).itcount();
   detail.asserts = collection.aggregate(
      { $match : filter },
      { $unwind : "$set" }, 
      { $group : { _id : "$set" } } 
   ).itcount();
   detail.assertInCloneRatio = detail.asserts/result.others.totalStaticCalls;
   detail.scores = collection.aggregate(
      { $match : filter },
      { $group : {_id : "$score", count_ : {$sum : 1} } },
      { $sort : {_id : -1} },
      { $project : {_id : 0, score : "$_id", count : "$count_"} }
   ).toArray()
   detail.ccsizes = collection.aggregate(
      { $match : filter },
      { $group : {_id : "$ccsize", count_ : {$sum : 1} } }, 
      { $sort : {_id : -1} },
      { $project : {_id : 0, ccsize : "$_id", count : "$count_"} }
   ).toArray()
   detail.scoreAssertAvgs = collection.aggregate(
      { $match : filter },
      { $unwind : "$set" }, 
      { $group : {_id : {_id : "$_id", score : "$score"}, count_ : {$sum : 1} } },
      { $group : {_id : "$_id.score", avgcount_ : {$avg : "$count_"} } },
      { $sort : {_id : -1} },
      { $project : {_id : 0, score : "$_id", avgAssertSize : "$avgcount_"} }
   ).toArray()
   detail.ccsizeAssertAvgs = collection.aggregate(
      { $match : filter },
      { $unwind : "$set" }, 
      { $group : {_id : {_id : "$_id", ccsize : "$ccsize"}, count_ : {$sum : 1} } },
      { $group : {_id : "$_id.ccsize", avgcount_ : {$avg : "$count_"} } },
      { $sort : {_id : -1} },
      { $project : {_id : 0, ccsize : "$_id", avgAssertSize : "$avgcount_"} }
   ).toArray()
   result.details.push(detail);
}
printjson(result);
