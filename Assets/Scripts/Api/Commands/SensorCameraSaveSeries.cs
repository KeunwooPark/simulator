/**
* Copyright (c) 2019 LG Electronics, Inc.
*
* This software contains code licensed as described in LICENSE.
*
*/

using SimpleJSON;
using UnityEngine;
using UnityEngine.PostProcessing;
using System;

namespace Api.Commands
{
    class SensorCameraSaveSeries : ICommand
    {
        public string Name { get { return "sensor/camera/save_series"; } }

        public void Execute(JSONNode args)
        {
            var uid = args["uid"].Value;

            Component sensor;
            if (ApiManager.Instance.Sensors.TryGetValue(uid, out sensor))
            {
                if (sensor is VideoToROS)
                {
                    var camera = sensor as VideoToROS;
                    var dirPath = args["dir"].Value;
                    var imgId = args["iid"].AsInt;
                    var quality = args["quality"].AsInt;
                    var compression = args["compression"].AsInt;

                    var pp = camera.GetComponent<PostProcessingBehaviour>();
                    bool oldpp = false;
                    if (pp != null)
                    {
                        oldpp = pp.profile.motionBlur.enabled;
                        pp.profile.motionBlur.enabled = false;
                    }

                    var imgFileName = dirPath + "/" + imgId.ToString() + ".jpeg";
                    var timeFileName = dirPath + "/" + imgId.ToString() + ".txt";
                    bool saveResult = camera.SaveAsync(imgFileName, timeFileName, quality, compression);

                    var result = new JSONObject();
                    result.Add("success", "True");

                    if (pp != null)
                    {
                        pp.profile.motionBlur.enabled = oldpp;
                    }
                    ApiManager.Instance.SendResult(result);
                }
                else
                {
                    ApiManager.Instance.SendError($"Sensor '{uid}' is not a camera sensor");
                }
            }
            else
            {
                ApiManager.Instance.SendError($"Sensor '{uid}' not found");
            }
        }
        private static System.Random random = new System.Random();
        private static string RandomString(int length)
        {
            const string chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
            char[] randomString = new char[length];
            for(int i=0; i<length; i++)
            {
              randomString[i] = chars[random.Next(chars.Length)];
            }
            return new String(randomString);
        }
    }
}
